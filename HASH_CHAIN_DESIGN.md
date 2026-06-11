# マルチレイヤーハッシュチェーン管理システム

## 概要

**デバッグ・ロールバック・復旧** の3パターンを独立した不変チェーンで管理するシステム。

```
Main Chain (本番・不動)
     ↓
Debug Chain (デバッグ検証・新規ハッシュ)
     ├─ Rollback Chain (→新規ハッシュ鎖・ロールバック復旧)
     └─ Recovery Chain (→新規ハッシュ鎖・通常復旧)
```

### 特徴

1. **不変性 (Immutability)** - ハッシュチェーン理論に基づく改ざん防止
2. **分岐対応** - 各パターンは独立した新規ハッシュチェーンを形成
3. **親参照** - デバッグチェーンのハッシュを参照（トレーサビリティ）
4. **破棄対応** - チェーン破棄時はメタデータのみ保持
5. **検証機構** - 全チェーンの一貫性を検証可能

---

## アーキテクチャ

### チェーンの階層構造

```
Tier 0: Main Chain (本番)
  └─ 3ブロック (v1.0, v1.1, v1.2)
  └─ Hash: edf5762556a3d931...

Tier 1: Debug Chain (デバッグ)
  └─ 2ブロック (v2.0, v2.1)
  └─ Parent Hash: edf5762556a3d931...
  └─ Chain Hash: 0dca8f5fe0286628...
  
Tier 2a: Rollback Chain
  └─ 1ブロック (Main系統に復旧)
  └─ Parent Hash: 0dca8f5fe0286628...
  
Tier 2b: Recovery Chain
  └─ 1ブロック (Debug系統を復旧)
  └─ Parent Hash: 0dca8f5fe0286628...
```

### ブロック構造

```python
ChainBlock {
    index: int                          # ブロック番号
    timestamp: str                      # タイムスタンプ
    data: Dict                          # ペイロード
    previous_hash: str                  # 前ブロックのハッシュ（チェーン連鎖）
    parent_chain_hash: Optional[str]    # 親チェーンのハッシュ（分岐追跡）
    chain_type: str                     # main|debug|rollback|recovery
    state: str                          # valid|pending|invalid|rolled_back|recovered|discarded
    hash: str                           # このブロックのハッシュ
}
```

### ハッシュ計算方式

```
block_hash = SHA256(JSON({
    index,
    timestamp,
    data,
    previous_hash,
    parent_chain_hash,
    chain_type
}))
```

**特点**: データとメタデータを含めてハッシュ化 → 改ざん検出可能

---

## チェーンのライフサイクル

### 1. Main Chain（本番チェーン）

```
初期化 → Add Block → Add Block → Add Block → (固定・不変)

役割: 本番環境の記録
状態: 常にVALID
破棄: 不可（ルートチェーン）
```

### 2. Debug Chain（デバッグチェーン）

```
Main → 新規ハッシュチェーン開始 → Block A → Block B → (検証)

特徴:
  - Main Chainの最後のブロックハッシュを参照
  - 独立したハッシュチェーンを形成
  - 新しいデータを実験的に追加可能
  - 検証後、Rollback/Recovery Chainに分岐
  - または破棄
```

### 3. Rollback Chain（ロールバック用）

```
Debug Chain → 新規ハッシュチェーン → 特定インデックスまで復旧 → 新規チェーン

用途: エラー発生時に特定ポイントまで戻す
データ: Debug Chainの一部を「action: rollback」で再構成
特点: Main Chainより先のブロックは含まない
```

### 4. Recovery Chain（復旧用）

```
Debug Chain → 新規ハッシュチェーン → 指定インデックス以降を復旧 → 新規チェーン

用途: 部分的なエラー復旧・続行
データ: Debug Chainの一部を「action: recovery」で再構成
特点: 部分的に復旧可能（index以降のみ）
```

### 5. Discarded Chain（破棄）

```
Debug/Rollback/Recovery Chain → metadata only保持 → 削除

保持情報:
  - chain_type, blocks_count
  - chain_hash（検証用）
  - parent_chain_hash（トレーサビリティ）
  - discarded_at（タイムスタンプ）

利用: 監査ログ・復旧分析
```

---

## 運用フロー

### シナリオ1: デバッグ→承認→本番反映

```
1. Main Chain作成（本番ブロック）
2. Debug Chain作成（Main参照）
3. Debug Chainにテストデータ追加
4. Debug Chainを検証
5. 承認 → Main Chainに統合
6. Debug Chain破棄
```

### シナリオ2: デバッグ→エラー→ロールバック

```
1. Debug Chainでエラー検出（Block 2で失敗）
2. Rollback Chain作成（Debug参照、index=1までロールバック）
3. Rollback Chainから復旧
4. Debug Chain破棄
5. Rollback Chain検証 → 本番に適用
```

### シナリオ3: デバッグ→部分復旧→続行

```
1. Debug Chainで複数ブロック追加（Block 0-3）
2. Block 1でエラー検出
3. Recovery Chain作成（Debug参照、index=2以降を復旧）
4. Recovery Chainから続行
5. Debug Chain破棄
```

---

## 検証メカニズム

### チェーン内の検証

```python
def validate_chain():
    # 1. 親チェーン参照の確認
    if parent_chain_hash != 親チェーンの最後のハッシュ:
        ERROR("親参照が一致しない")
    
    # 2. ブロック連鎖の確認
    for each block:
        if block.previous_hash != 前ブロック.hash:
            ERROR("ブロック連鎖が断裂")
        if SHA256(block) != block.hash:
            ERROR("ハッシュが改ざんされている")
    
    return is_valid
```

### 全チェーン検証

```
Main Chain ✓ VALID
  ↓
Debug Chain ✓ VALID (Main参照OK)
  ↓
├─ Rollback Chain ✓ VALID (Debug参照OK)
└─ Recovery Chain ✓ VALID (Debug参照OK)
```

---

## ハッシュ破棄パターンの分析

### パターン1: 即座破棄（即回収）

```
Debug Chain作成 → エラー検出 → 即座に破棄
  - ストレージコスト: 最小
  - トレーサビリティ: 低い（メタデータのみ）
  - 用途: 開発環境の試験用
```

### パターン2: ロールバック後破棄

```
Debug Chain → Rollback Chain → 検証成功 → Debug Chain破棄
  - Rollback Chainは保持（復旧記録）
  - Debug ChainのハッシュはMetadataで保持
  - トレーサビリティ: 中程度
```

### パターン3: 監査後破棄

```
Debug Chain → 監査ログ記録 → 検証 → 署名 → 破棄
  - メタデータ（chain_hash, parent_chain_hash）は永続保存
  - 改ざんされていないことを証明可能
  - トレーサビリティ: 高い（署名付き）
```

### パターン4: アーカイブ破棄

```
Debug Chain → 圧縮 → Zstandard圧縮 → S3/アーカイブ → 破棄
  - ストレージ削減（gzip比 50%）
  - トレーサビリティ: 最高（完全記録）
  - 用途: 長期監査・コンプライアンス
```

### 破棄時のメタデータ保持

```json
{
  "chain_type": "debug",
  "blocks_count": 5,
  "chain_hash": "0dca8f5fe0286628...",
  "parent_chain_hash": "edf5762556a3d931...",
  "discarded_at": "2026-06-11T04:23:54.791928",
  "reason": "test_complete|error_recovery|archive",
  "signature": "optional_ed25519_signature"
}
```

---

## 実装の利点

### 1. タンパープルーフ（改ざん防止）

```
ハッシュチェーン理論により:
  - データ変更 → ハッシュ変更 → 全後続ブロックが無効化
  - 改ざん検出率: 100%
```

### 2. 監査可能性（Auditability）

```
全ての分岐経路が追跡可能:
  main.hash → debug.hash → {rollback.hash | recovery.hash}
  
チェーングラフにより:
  - どのような復旧経路を取ったかが明確
  - 各段階での状態が記録
```

### 3. 段階的リカバリ

```
従来: 本番 → エラー → 全ロールバック
改善: 本番 → デバッグ → 部分ロールバック → 復旧 → 続行
```

### 4. メモリ効率

```
破棄時にデータ削除:
  - メタデータのみ保持（JSON 500 byte）
  - 実データ削除（数MB～GB削減）
  - チェーン検証は常に可能（ハッシュ値から）
```

---

## GitHub用の実装パターン

```
error-handling-debug-system/
├── debug_framework/
│   ├── __init__.py
│   └── ... (既存)
│
├── hash_chain/
│   ├── __init__.py
│   ├── multi_layer_hash_chain.py    ← このモジュール
│   ├── chain_validator.py           ← 検証エンジン
│   └── chain_persistence.py         ← SQLite永続化
│
├── tests/
│   ├── test_multi_layer_hash_chain.py
│   └── test_chain_scenarios.py      ← 運用シナリオテスト
│
├── docs/
│   └── HASH_CHAIN_DESIGN.md         ← このドキュメント
│
└── examples/
    ├── example_debug_rollback.py
    └── example_recovery_flow.py
```

---

## API リファレンス

### MultiChainManager

```python
# 初期化
manager = MultiChainManager()

# Main Chainに追加
block = manager.add_to_main({'version': 'v1.0'})

# Debug Chainを作成
debug_chain = manager.create_debug_chain()

# Rollback Chain を作成（index までロールバック）
rollback_chain = manager.create_rollback_chain(
    debug_chain_id='debug_1',
    rollback_to_index=2
)

# Recovery Chain を作成（from_index 以降を復旧）
recovery_chain = manager.create_recovery_chain(
    debug_chain_id='debug_1',
    from_index=1
)

# チェーン検証
results = manager.validate_all_chains()

# チェーン破棄
discarded = manager.discard_chain('debug_1')

# 統計情報
stats = manager.get_chain_stats()

# エクスポート
export = manager.export_chains()
```

---

## パフォーマンス

### タイムコンプレキシティ

| 操作 | 計算量 | 説明 |
|------|------|------|
| Add Block | O(1) | SHA256計算（定時間） |
| Validate Chain | O(n) | n=ブロック数 |
| Validate All | O(m×n) | m=チェーン数, n=平均ブロック数 |
| Discard | O(1) | メタデータ記録のみ |

### スペースコンプレキシティ

| 項目 | サイズ |
|------|--------|
| Block (ペイロード除き) | ~400 bytes |
| Chain Metadata | ~300 bytes |
| Discarded Chain Record | ~500 bytes |

---

**最終更新**: 2026-06-11  
**バージョン**: 1.0.0
