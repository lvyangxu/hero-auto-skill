# 事务官自动分配技能点（AutoSkillPointsForAgents）

一个《全面战争：战锤3》（Total War: WARHAMMER III）的脚本 Mod。

## 它做什么

当事务官（英雄、法师、刺客等 agent）出现下列情况时，自动帮你勾选角色技能树**左上角的「自动分配技能点数」复选框**：

- 被**招募**或**召唤**到战役地图上时；
- 从**受伤中恢复**、重新回到战役地图时。

勾选后，该角色升级获得的技能点会按游戏默认逻辑自动分配，省去逐个手动点选的麻烦。

## 触发时机（事件驱动）

本 Mod **完全基于事件触发，不扫描、不轮询**整个角色列表，只对游戏明确告知的角色发出指令：

| 事件 | 说明 |
| --- | --- |
| `CharacterCreated` | 角色被创建（招募、召唤、脚本生成等） |
| `CharacterRecruited` | 从招募池招募 |
| `UniqueAgentSpawned` | 特殊 / 传奇事务官被召唤 |
| `CharacterExitsLimboEvent` | 角色离开 limbo、回到地图（例如受伤恢复） |

## 生效范围

- 只影响**玩家（本地派系）**的**事务官 / 英雄**（`cm:char_is_agent`）。
- 不会影响领主、大臣等非事务官单位，也不会影响 AI 派系。

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
src/      Mod 源码（Lua 脚本）
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
