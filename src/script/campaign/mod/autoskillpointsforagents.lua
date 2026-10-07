--====================================================================--
--  Agent Auto Skill Management      (autoskillpointsforagents v1.2.0)
--====================================================================--
--  Automatically ticks the "Auto allocate skill points" checkbox (the one
--  at the top-left of the character skill tree) for the player's
--  agents / heroes whenever they are:
--      * recruited or summoned onto the map, and
--      * recovered from being wounded (they exit limbo and return to
--        the campaign map).
--
--  This mod is purely event driven: it never scans or polls the whole
--  character list, so it only ever issues context commands for the exact
--  characters the game tells us about.
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

local ASPA_VERSION    = "1.2.0";
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

	if faction:is_human() then
		-- single player, or the local player in a multiplayer campaign
		return true;
	end;

	return faction:name() == cm:get_local_faction_name();
end;

-- Only the player's agents / heroes should be affected (never lords,
-- colonels or ministers, which are not "agents").
local function aspa_should_auto_manage(character)
	if not aspa_is_valid_character(character) then
		return false;
	end;

	if not aspa_is_local_faction(character:faction()) then
		return false;
	end;

	if not cm:char_is_agent(character) then
		return false;
	end;

	return true;
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

	if set_ok then
		aspa_out("enabled auto skill allocation for character " .. tostring(cqi));
	else
		aspa_out("could not enable auto skill allocation for character "
			.. tostring(cqi) .. ": " .. tostring(err));
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

	aspa_out("v" .. ASPA_VERSION .. " loaded");
end;
