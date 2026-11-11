-- test_ui_graph.lua — The graph view's gamepad input (UIGraph.handle_view_input)
local lu = require("luaunit")

-- ui_graph.lua requires calc_graph and reads picocalc.gamepad when it loads.
package.path = "../?.lua;" .. package.path

-- The firmware's PAD_* values (PicoDeck src/os/os.h), and getLabel answering
-- from `labels`: the default keys, which a test may rebind.
local PAD = {PAD_UP = 1, PAD_DOWN = 2, PAD_LEFT = 4, PAD_RIGHT = 8,
             PAD_A = 16, PAD_B = 32, PAD_L = 256, PAD_R = 512}
local labels
PAD.getLabel = function(btn) return labels[btn] end

-- A fresh module (its mode and viewport are module state), loaded with a
-- stub picocalc.gamepad that is taken away again afterwards.
local function load_ui_graph()
    picocalc = {gamepad = PAD}
    local UIGraph = dofile("../ui_graph.lua")
    picocalc = nil
    return UIGraph
end

TestUIGraphPad = {}

function TestUIGraphPad:setUp()
    labels = {[1] = "Up", [2] = "Down", [4] = "Left", [8] = "Right", [16] = "F4"}
    self.ui = load_ui_graph()
    self.ui.handle_action("cmd:graph_view", "")
    self.vp = self.ui.get_graph().viewport
end

function TestUIGraphPad:test_view_dpad_pans()
    lu.assertTrue(self.ui.handle_view_input(PAD.PAD_RIGHT, ""))
    lu.assertAlmostEquals(self.vp.xmin, -8, 1e-6)
    lu.assertTrue(self.ui.handle_view_input(PAD.PAD_UP, ""))
    lu.assertAlmostEquals(self.vp.ymin, -8, 1e-6)
end

function TestUIGraphPad:test_view_a_traces_and_a_again_returns()
    lu.assertTrue(self.ui.handle_view_input(PAD.PAD_A, ""))
    lu.assertEquals(self.ui.get_mode(), "trace")
    lu.assertTrue(self.ui.handle_view_input(PAD.PAD_A, ""))
    lu.assertEquals(self.ui.get_mode(), "view")
end

function TestUIGraphPad:test_table_a_returns_to_view()
    self.ui.handle_action("cmd:graph_table", "")
    lu.assertTrue(self.ui.handle_view_input(PAD.PAD_A, ""))
    lu.assertEquals(self.ui.get_mode(), "view")
end

function TestUIGraphPad:test_b_l_r_and_nothing_are_left_to_main()
    -- B leaves the graph view and L/R step the tabs: main.lua's to handle.
    for _, nav in ipairs({0, PAD.PAD_B, PAD.PAD_L, PAD.PAD_R}) do
        lu.assertFalse(self.ui.handle_view_input(nav, ""))
    end
    lu.assertEquals(self.ui.get_mode(), "view")
    lu.assertAlmostEquals(self.vp.xmin, -10, 1e-6)
end

-- A display that keeps the text drawn on the hint row (y = 294).
local function hint_of(draw)
    local d = setmetatable({}, {__index = function() return function() return 0 end end})
    d.textWidth = function(t) return #t * 6 end
    d.drawText = function(_, y, t) if y == 294 then d.hint = t end end
    draw(d, nil)
    return d.hint
end

function TestUIGraphPad:test_hints_name_the_bound_keys()
    lu.assertEquals(hint_of(self.ui.draw_view),
                    "Arrows:pan +/-:zoom R:reset I:input T:table F4:trace")
    lu.assertEquals(hint_of(self.ui.draw_trace), "Left/Right:move Up/Down:func F4/Esc:back")
    lu.assertEquals(hint_of(self.ui.draw_table), "Up/Down:scroll Left/Right:step F4/Esc:back")
end

function TestUIGraphPad:test_hints_follow_a_rebind()
    labels[16] = "Z"          -- A rebound to Z while the app runs
    lu.assertEquals(hint_of(self.ui.draw_view),
                    "Arrows:pan +/-:zoom R:reset I:input T:table Z:trace")
    labels[16] = nil          -- A left unbound
    lu.assertEquals(hint_of(self.ui.draw_trace), "Left/Right:move Up/Down:func ?/Esc:back")
end
