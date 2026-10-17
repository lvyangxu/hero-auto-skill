-- =====================================================================
--  AutoSkillPointsForAgents - MCT settings page
--  (script/mct/settings/autoskillpointsforagents_settings.lua)
-- =====================================================================
--  Registers the mod in the "Mod Configuration Tool" (MCT) so the player
--  can choose, per character category, whether skill points should be
--  auto-allocated:
--
--      * agents / heroes  : ON  by default (original behaviour)
--      * lords / generals : OFF by default
--
--  MCT automatically loads every *.lua file placed under
--  script/mct/settings/, so this file needs NO entry function of its own.
--  The main script reads the values back with:
--
--      get_mct():get_mod_by_key(<mod_key>)
--               :get_option_by_key(<option_key>)
--               :get_selected_setting()
--====================================================================--

-- MCT is optional: when it is not installed `get_mct` is nil and we bail,
-- leaving the mod on its built-in defaults (agents on, lords off).
if not get_mct then
	return;
end;

local mct = get_mct();

local mod = mct:register_mod("auto_skill_points_for_agents");
mod:set_title("事务官 / 领主自动分配技能点");
mod:set_author("chashaobao");
mod:set_description("自动勾选角色技能树左上角的「自动分配技能点数」。可分别控制事务官与领主，默认只对事务官开启。");

local agents = mod:add_new_option("auto_agents", "checkbox");
agents:set_default_value(true);
agents:set_text("事务官自动分配技能点");
agents:set_tooltip_text("事务官被招募 / 召唤，或从受伤中恢复、重新回到地图时，自动为其勾选「自动分配技能点数」。默认开启。");

local lords = mod:add_new_option("auto_lords", "checkbox");
lords:set_default_value(false);
lords:set_text("领主自动分配技能点");
lords:set_tooltip_text("领主被招募 / 创建，或从受伤中恢复、重新回到地图时，自动为其勾选「自动分配技能点数」。默认关闭。");

-- =====================================================================
-- NOTE: the one-click equipment options that used to live here have moved
-- to the standalone mod "AutoEquipRareAncillaries", see its own
-- script/mct/settings/auto_equip_rare_ancillaries_settings.lua.
-- =====================================================================
