# 事务官 / 领主自动分配技能点（AutoSkillPointsForAgents）

一个《全面战争：战锤3》（Total War: WARHAMMER III）的脚本 Mod。

## 它做什么

当事务官（英雄、法师、刺客等 agent）出现下列情况时，自动帮你勾选角色技能树**左上角的「自动分配技能点数」复选框**：

- 被**招募**或**召唤**到战役地图上时；
- 从**受伤中恢复**、重新回到战役地图时。

默认**只对事务官生效**；领主 / 将军可在配置菜单中单独开启（见下）。

勾选后，该角色升级获得的技能点会按游戏默认逻辑自动分配，省去逐个手动点选的麻烦。

> **「一键装备蓝色装备」已拆分为独立 Mod**（`AutoEquipRareAncillaries`）。
> 本 Mod 现在只负责「自动分配技能点」这一件事，两个 Mod 可以分开启用 / 停用。

## 触发时机（事件驱动）

本 Mod **完全基于事件触发，不扫描、不轮询**整个角色列表，只对游戏明确告知的角色发出指令：

| 事件 | 说明 |
| --- | --- |
| `CharacterCreated` | 角色被创建（招募、召唤、脚本生成等） |
| `CharacterRecruited` | 从招募池招募 |
| `UniqueAgentSpawned` | 特殊 / 传奇事务官被召唤 |
| `CharacterExitsLimboEvent` | 角色离开 limbo、回到地图（例如受伤恢复） |

例外：**首次进入本地回合时会补扫一次**当前派系的角色列表。中途安装脚本 Mod 时，已有角色不会触发上面任何一个事件，这一次补扫只为把他们补上；监听器随后自动移除（`persistent = false`），之后仍然完全事件驱动。

## 生效范围

- 只影响**玩家（本地派系）**的角色，不会影响 AI 派系。
- **事务官 / 英雄**（`cm:char_is_agent`）：默认开启自动分配。
- **领主 / 将军**（`cm:char_is_general`）：默认关闭，可在配置菜单中开启。
- 不会影响大臣（minister）等其它类型单位。

## 配置（Mod Configuration Tool / MCT）

本 Mod 支持 **mod configuration tools**（MCT）配置菜单：

| 选项 | 默认 | 说明 |
| --- | --- | --- |
| 事务官自动分配技能点 | **开** | 招募 / 召唤事务官，或事务官受伤恢复时自动勾选 |
| 领主自动分配技能点 | **关** | 领主被创建 / 招募，或受伤恢复时自动勾选 |

未安装 MCT 时，Mod 使用上述内置默认值，功能照常工作。

## 实现原理

「自动分配技能点数」复选框由战役 UI 上下文对象 `CcoCampaignCharacterAutoManagement` 驱动，可从角色经 `AutoManagementContext` 属性访问。脚本通过引擎辅助函数读取 / 切换它：

```lua
-- 读取当前状态
common.get_context_value("CcoCampaignCharacter", cqi, "AutoManagementContext.IsAutoManaging")
-- 切换开启
common.call_context_command("CcoCampaignCharacter", cqi, "AutoManagementContext.ToggleAutoManaging()")
```

先读后写：仅在该复选框处于关闭状态时才切换，**绝不会把已经开启的关掉**。

## 安装

- **创意工坊订阅**：在 Steam 创意工坊订阅本 Mod 即可。
- **手动安装**：把 `AutoSkillPointsForAgents.pack` 放入游戏目录：

  ```
  <游戏安装目录>\Total War WARHAMMER III\data\
  ```

  建议同时放入同名缩略图 `AutoSkillPointsForAgents.png`。

## 兼容性

- 纯脚本 Mod，采用事件驱动，与其他 Mod 冲突的可能性很低。

## 目录结构

```
src/
  script/campaign/mod/autoskillpointsforagents.lua          自动分配技能点
dist/     打包好的 .pack 与缩略图
tools/    构建 / 解析辅助脚本（不随 Mod 发布）
```

## 自行构建

```
python tools/build_pack.py src dist/AutoSkillPointsForAgents.pack
```

> 开发提示：引擎会把 pack 内的路径统一转成小写，再调用与（小写）文件名同名的全局入口函数。
> 因此脚本文件 `autoskillpointsforagents.lua` 与入口函数 `autoskillpointsforagents()` 必须保持**全小写且一致**，否则 Mod 会静默失效。

## 许可证

见 [LICENSE](LICENSE)。
