--====================================================================--
--  Agent Auto Skill Management      (autoskillpointsforagents v1.4.1)
--====================================================================--
--  Automatically ticks the "Auto allocate skill points" checkbox (the one
--  at the top-left of the character skill tree) for the player's
--  characters whenever they are:
--      * recruited or summoned onto the map, and
--      * recovered from being wounded (they exit limbo and return to
--        the campaign map).
--
--  Which characters are affected is configurable through the
--  "Mod Configuration Tool" (MCT), when it is installed:
--      * agents / heroes  : ON  by default (original behaviour)
--      * lords / generals : OFF by default
--  The toggles live in
--  script/mct/settings/autoskillpointsforagents_settings.lua.
--
--  The mod is event driven: it never polls the whole character list, it
--  only reacts to the characters the game tells us about.  One single
--  sweep of the local faction is done on the first local turn so that
--  characters that already existed when the mod was installed are picked
--  up as well (installing a script mod mid campaign fires no events for
--  characters that were created before it was loaded).
--
--  This mod is intentionally scoped to skill point allocation only.  The
--  one-click equipment feature was split off into its own mod
--  "AutoEquipRareAncillaries" (script/campaign/mod/auto_equip_rare_ancillaries.lua)
--  so that the two can be enabled independently.
--
--  How it works
--  ------------
--  The checkbox is driven by the campaign UI context object
--  "CcoCampaignCharacterAutoManagement", which is reached from a character
--  through the "AutoManagementContext" property.  Its state can be read and
--  toggled from script with the engine helpers common.get_context_value()
--  and common.call_context_command(), exactly like the base game does for
--  e.g. "CcoBattleRoot -> TimeControlContext.SetCanChangeTime(true)".
--
--      read :  common.get_context_value("CcoCampaignCharacter", cqi,
--                                       "AutoManagementContext.IsAutoManaging")
--      set  :  common.call_context_command("CcoCampaignCharacter", cqi,
--                                       "AutoManagementContext.ToggleAutoManaging()")
--
--  IMPORTANT: the engine lower-cases the file path it finds inside the pack
--  and then calls the global function of that (lower-cased) name.  So the
--  file is named autoskillpointsforagents.lua and the entry point below is
--  autoskillpointsforagents() - both must stay all lower case or the mod
--  silently never runs ("autoskillpointsforagents() not found").
--====================================================================--

-- You can set this global to false in a personal copy of the file if you
-- ever want to stop the script from (re-)enabling auto-management.
if auto_skill_points_for_agents_enabled == nil then
	auto_skill_points_for_agents_enabled = true;
end;

local ASPA_VERSION    = "1.4.1";
local ASPA_LOG_PREFIX = "[autoskillpointsforagents] ";

local function aspa_out(msg)
	local text = ASPA_LOG_PREFIX .. tostring(msg);
	out(text);
	-- ModLog() is provided by the base game mod loader; write to
	-- lua_mod_log.txt as well so the mod's activity can be checked easily.
	if ModLog ~= nil then
		ModLog(text);
	end;
end;


----------------------------------------------------------------------
-- Mod Configuration Tool (MCT) integration
----------------------------------------------------------------------
-- These keys MUST match
-- script/mct/settings/autoskillpointsforagents_settings.lua.
-- When MCT is not installed (get_mct == nil) the mod falls back to the
-- built-in defaults below, i.e. agents enabled and lords disabled.

local ASPA_MCT_MOD_KEY       = "auto_skill_points_for_agents";
local ASPA_MCT_OPTION_AGENTS = "auto_agents";
local ASPA_MCT_OPTION_LORDS  = "auto_lords";

-- Read a checkbox value from MCT, returning `fallback` whenever MCT (or
-- the option) is unavailable for any reason, so the mod keeps working
-- even without MCT installed.
local function aspa_mct_get(option_key, fallback)
	if get_mct == nil then
		return fallback;
	end;

	local ok, value = pcall(function()
		local mct = get_mct();
		local mod = mct:get_mod_by_key(ASPA_MCT_MOD_KEY);
		if mod == nil then
			return nil;
		end;

		local option = mod:get_option_by_key(option_key);
		if option == nil then
			return nil;
		end;

		return option:get_selected_setting();
	end);

	if ok and value ~= nil then
		return value;
	end;

	return fallback;
end;


----------------------------------------------------------------------
-- helpers
----------------------------------------------------------------------

-- null / invalid guard for the character interface
local function aspa_is_valid_character(character)
	return character ~= nil and character:is_null_interface() == false;
end;

-- is this character owned by the player (local) faction?
local function aspa_is_local_faction(faction)
	if faction == nil or faction:is_null_interface() then
		return false;
	end;

	-- the local player's faction, in single player as well as in a
	-- multiplayer campaign (where other human factions are "human" too
	-- but must not be touched)
	if faction:name() == cm:get_local_faction_name() then
		return true;
	end;

	return faction:is_human();
end;

-- Classify a character the mod can handle:
--   "agent" - heroes / agents (cm:char_is_agent)
--   "lord"  - lords / generals (cm:char_is_general)
--   nil     - anything else (colonels, ministers, ...), which is ignored.
local function aspa_get_category(character)
	if cm:char_is_agent(character) then
		return "agent";
	end;

	if cm:char_is_general(character) then
		return "lord";
	end;

	return nil;
end;

-- Should this character get its auto-management flag turned on?  Only the
-- player's (local faction) characters are considered, and each category
-- is gated behind its own MCT toggle (agents on / lords off by default).
local function aspa_should_auto_manage(character)
	if not aspa_is_valid_character(character) then
		return false;
	end;

	if not aspa_is_local_faction(character:faction()) then
		return false;
	end;

	local category = aspa_get_category(character);

	if category == "agent" then
		return aspa_mct_get(ASPA_MCT_OPTION_AGENTS, true);
	elseif category == "lord" then
		return aspa_mct_get(ASPA_MCT_OPTION_LORDS, false);
	end;

	return false;
end;

-- Turn the auto-management flag ON for a character.  Never turns it off,
-- and never touches a character that is not a valid local agent.
local function aspa_enable_auto_management(character)
	if not auto_skill_points_for_agents_enabled then
		return;
	end;

	if not aspa_should_auto_manage(character) then
		return;
	end;

	local cqi = character:command_queue_index();

	-- Read current state first so we never accidentally toggle it OFF.
	local read_ok, is_on = pcall(function()
		return common.get_context_value(
			"CcoCampaignCharacter", cqi,
			"AutoManagementContext.IsAutoManaging"
		);
	end);

	if read_ok and is_on == true then
		return;  -- already enabled, nothing to do
	end;

	local set_ok, err = pcall(function()
		common.call_context_command(
			"CcoCampaignCharacter", cqi,
			"AutoManagementContext.ToggleAutoManaging()"
		);
	end);

	local category = aspa_get_category(character);

	if set_ok then
		aspa_out("enabled auto skill allocation for " .. tostring(category)
			.. " " .. tostring(cqi));
	else
		aspa_out("could not enable auto skill allocation for " .. tostring(category)
			.. " " .. tostring(cqi) .. ": " .. tostring(err));
	end;
end;

-- Same as above, but also retries once on a later tick.  A freshly created
-- character is not always fully present in the campaign UI context on the
-- very first frame, so the short retry makes the behaviour reliable.
local function aspa_enable_for_character(character)
	if not aspa_should_auto_manage(character) then
		return;
	end;

	aspa_enable_auto_management(character);

	cm:callback(
		function()
			aspa_enable_auto_management(character);
		end,
		0.5
	);
end;

----------------------------------------------------------------------
-- one-off catch-up sweep
----------------------------------------------------------------------
-- Installing a script mod into a running campaign fires no CharacterCreated
-- / CharacterRecruited event for the characters that already exist, so
-- those would never get the checkbox ticked.  On the very first local turn
-- we therefore walk the local faction's character list once and treat each
-- character like a freshly created one.
--
-- The listener removes itself (persistent = false) after the first local
-- turn, so there is no per-turn polling afterwards - the mod stays
-- event driven.

local aspa_initial_sweep_done = false;

local function aspa_do_initial_sweep(faction)
	if aspa_initial_sweep_done then
		return;
	end;

	if not aspa_is_local_faction(faction) then
		return;
	end;

	aspa_initial_sweep_done = true;

	local count = 0;

	local characters = faction:character_list();
	for i = 0, characters:num_items() - 1 do
		local character = characters:item_at(i);
		if aspa_should_auto_manage(character) then
			aspa_enable_auto_management(character);
			count = count + 1;
		end;
	end;

	aspa_out("initial sweep of " .. tostring(faction:name())
		.. ": checked " .. tostring(count) .. " character(s)");
end;


----------------------------------------------------------------------
-- entry point - called automatically on the first campaign tick.
-- NOTE: name MUST equal the (lower-cased) file name, i.e. all lower case.
----------------------------------------------------------------------

function autoskillpointsforagents()

	-- A character is created (recruited, summoned, scripted spawn, ...).
	core:add_listener(
		"autoskillpointsforagents_character_created",
		"CharacterCreated",
		true,
		function(context)
			aspa_enable_for_character(context:character());
		end,
		true
	);

	-- A character is recruited from the recruitment pool.
	core:add_listener(
		"autoskillpointsforagents_character_recruited",
		"CharacterRecruited",
		true,
		function(context)
			aspa_enable_for_character(context:character());
		end,
		true
	);

	-- A unique / legendary agent is summoned.
	core:add_listener(
		"autoskillpointsforagents_unique_agent_spawned",
		"UniqueAgentSpawned",
		true,
		function(context)
			local details = context:unique_agent_details();
			if details ~= nil then
				aspa_enable_for_character(details:character());
			end;
		end,
		true
	);

	-- A character came back onto the map, e.g. a hero recovering from its
	-- wounds ("exiting limbo").  This replaces the old per-turn scan.
	core:add_listener(
		"autoskillpointsforagents_character_exits_limbo",
		"CharacterExitsLimboEvent",
		true,
		function(context)
			aspa_enable_for_character(context:character());
		end,
		true
	);

	-- First local turn: pick up characters that existed before the mod was
	-- installed.  Non-persistent, so it is gone after that single turn.
	core:add_listener(
		"autoskillpointsforagents_initial_sweep",
		"FactionTurnStart",
		true,
		function(context)
			aspa_do_initial_sweep(context:faction());
		end,
		false
	);

	aspa_out("v" .. ASPA_VERSION .. " loaded");
end;
