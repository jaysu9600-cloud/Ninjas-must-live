# 忍者必須活 - 計分系統規格文件 (Score System Specification)

## 1. 功能描述
- **基礎計分**：玩家每存活 1 秒（1000 毫秒），分數增加。
- **成長計分**：每過 10 秒，每秒增加的分數額度會遞增（例如：前 10 秒每秒 +10，第 11-20 秒每秒 +20，依此類推）。
- **畫面顯示**：在遊戲畫面左上角顯示目前的分數與當前每秒得分。

## 2. 系統流程圖
```mermaid
graph TD
    A[遊戲開始] --> B[初始化計分變數]
    B --> C[進入遊戲主迴圈]
    C --> D{是否過了一秒?}
    D -- 是 --> E[增加當前分數]
    E --> F{是否過了十秒?}
    F -- 是 --> G[增加每秒得分額度]
    G --> H[更新畫面顯示]
    F -- 否 --> H
    D -- 否 --> H
    H --> C
    C --> I[碰撞結束]
    I --> J[顯示最終得分]
```

## 3. 循序圖
```mermaid
sequenceDiagram
    participant Game as 遊戲主引擎
    participant Timer as 計時器/Clock
    participant Score as 計分系統

    Game->>Timer: 取得當前時間(ticks)
    Timer-->>Game: 回傳 ticks
    Game->>Score: 檢查是否達 1 秒
    alt 達 1 秒
        Score->>Score: 分數 += 當前增量
        Game->>Score: 檢查是否達 10 秒
        alt 達 10 秒
            Score->>Score: 當前增量 += 遞增額
        end
    end
    Score-->>Game: 更新當前分數顯示
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
        +int start_ticks
        +int level_ticks
        +update_score(current_ticks)
        +draw_score(screen)
    }
    GameEngine "1" -- "1" ScoreSystem : 包含
```

## 5. 實作細節
- `score`: `int`，初始為 0。
- `increase_rate`: `int`，基礎每秒增加 10 分。
- `increase_step`: `int`，每 10 秒增加 10 分額外增量。
- `last_score_tick`: `int`，記錄上次計分的時間。
- `last_level_tick`: `int`，記錄上次提升增量的時間。