# 忍者必須活 - 系統規格文件 (System Specification)

## 1. 功能描述
- **基礎計分**：玩家每存活 1 秒（1000 毫秒），分數增加。
- **成長計分**：每過 10 秒，每秒增加的分數額度會遞增（例如：前 10 秒每秒 +10，第 11-20 秒每秒 +20，依此類推）。
- **生命值系統**：玩家初始有 3 顆心（生命值）。
- **碰撞機制**：當玩家觸碰到障礙物時，減少一顆心，並提供短暫的無敵時間防止連續扣血。
- **死亡機制**：當生命值歸零時，遊戲切換至「結束畫面」。
- **遊戲重啟**：在結束畫面中提供「重新開始」功能（例如按下 R 鍵或對應圖標）。
- **多樣化障礙物**：障礙物不再是簡單的矩形，而是隨機出現「手裏劍 (shuriken)」或「苦無 (kunai)」圖片。素材已由原先的 JPG 格式升級為 PNG 格式（支援透明度處理）。
- **畫面顯示**：
    - 左上角顯示目前的分數與當前每秒得分。
    - 分數下方顯示剩餘生命值（心形圖標或文字）。
    - 遊戲結束畫面：中央顯示 "GAME OVER"，下方顯示最終得分與 "按 R 重新開始"。
- **靈活跳躍控制**：
    - 玩家按下空白鍵時**立即起跳**。
    - 起跳後若持續按住空白鍵，角色會獲得額外的向上推力（長按增益），使跳躍高度更高。
    - 增益有最大時間限制（約 350 毫秒），超過時間或放開按鍵即停止增益。

## 2. 系統流程圖
```mermaid
graph TD
    A[遊戲開始] --> B[初始化計分與生命值變數]
    B --> C[進入遊戲主迴圈]
    C --> D{是否過了一秒?}
    D -- 是 --> E[增加當前分數]
    E --> F{是否過了十秒?}
    F -- 是 --> G[增加每秒得分額度]
    G --> H[檢測碰撞]
    F -- 否 --> H
    D -- 否 --> H
    H --> I{發生碰撞且非無敵狀態?}
    I -- 是 --> J[生命值 -1]
    J --> K[設定無敵時間]
    K --> L{生命值 <= 0?}
    L -- 是 --> M[進入結束畫面]
    L -- 否 --> N[更新畫面顯示]
    I -- 否 --> N
    N --> C
    M --> O{玩家按下 R?}
    O -- 是 --> B
    O -- 否 --> M
```

## 3. 循序圖
```mermaid
sequenceDiagram
    participant Game as 遊戲主引擎
    participant Timer as 計時器/Clock
    participant Score as 計分系統
    participant Health as 生命系統

    Game->>Timer: 取得當前時間(ticks)
    Timer-->>Game: 回傳 ticks

    rect rgb(200, 255, 200)
    Note over Game: 跳躍邏輯 (即時起跳 + 長按增益)
    alt 按下 Space
        Game->>Game: 立即觸發基礎跳躍 (Initial Jump)
        Game->>Game: 開啟長按增益旗標
    else 更新迴圈 (Update Loop)
        alt 旗標開啟且未過時限
            Game->>Game: 施加額外上升力道
        end
    else 放開 Space
        Game->>Game: 關閉長按增益旗標
    end
    end
    
    rect rgb(240, 240, 240)
    Note over Score: 計分邏輯
    Game->>Score: 檢查是否達 1 秒
    alt 達 1 秒
        Score->>Score: 分數 += 當前增量
        Game->>Score: 檢查是否達 10 秒
        alt 達 10 秒
            Score->>Score: 當前增量 += 遞增額
        end
    end
    end

    rect rgb(255, 230, 230)
    Note over Health: 生命邏輯
    Game->>Health: 檢測碰撞
    alt 發生碰撞且非無敵
        Health->>Health: 生命值 -= 1
        Health->>Health: 設定無敵計時器
        alt 生命值 <= 0
            Health-->>Game: 觸發遊戲結束
        end
    end
    end
    
    Score-->>Game: 更新當前分數顯示
    Health-->>Game: 更新當前生命顯示
```

## 4. 物件關聯圖 (UML)
```mermaid
classDiagram
    class GameEngine {
        +run()
        +update()
        +draw()
    }
    class ScoreSystem {
        +int current_score
        +int score_per_second
        +int last_score_tick
        +int last_rate_increase_tick
        +update_score(current_ticks)
        +draw_score(screen)
    }
    class HealthSystem {
        +int lives
        +int invulnerable_timer
        +bool is_invulnerable
        +take_damage()
        +update(dt)
        +draw_health(screen)
    }
    GameEngine "1" -- "1" ScoreSystem : 包含
    GameEngine "1" -- "1" HealthSystem : 包含
```

## 5. 實作細節
- **計分系統**：
    - `score`: `int`，初始為 0。
    - `increase_rate`: `int`，基礎每秒增加 10 分。
    - `increase_step`: `int`，每 10 秒增加 10 分額外增量。
- **生命值系統**：
    - `lives`: `int`，初始為 3。
    - `invincible_duration`: `int`，受到傷害後的無敵時間（例如 1500 毫秒）。
    - `last_damage_tick`: `int`，記錄上次受傷的時間，用於計算無敵狀態。