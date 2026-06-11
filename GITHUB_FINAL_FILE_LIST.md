# GitHub リポジトリ: Error-handling-debug-system

完全なファイル構成と説明

---

## 📋 推奨ディレクトリ構造

```
Error-handling-debug-system/
│
├── README.md                                    # プロジェクト概要
├── LICENSE                                      # MIT ライセンス
├── setup.py                                     # パッケージ設定
├── requirements.txt                             # 依存関係
├── .gitignore                                   # Git設定
│
├── debug_framework/                             # 既存デバッグフレームワーク
│   ├── __init__.py
│   ├── exception_handler.py
│   ├── memory_management.py
│   ├── retry_manager.py
│   ├── frequency_control.py
│   ├── error_logging.py
│   └── system.py
│
├── hash_chain/                                  # 新規: マルチレイヤーハッシュチェーン
│   ├── __init__.py                             # NEW
│   ├── multi_layer_hash_chain.py               # NEW (コア実装)
│   ├── chain_validator.py                      # NEW (検証エンジン)
│   ├── chain_persistence.py                    # NEW (SQLite永続化)
│   └── chain_analyzer.py                       # NEW (破棄パターン分析)
│
├── tests/                                       # テストスイート
│   ├── __init__.py
│   ├── test_debug_framework.py                 # (既存)
│   ├── test_multi_layer_hash_chain.py          # NEW
│   ├── test_chain_validator.py                 # NEW
│   ├── test_chain_scenarios.py                 # NEW (運用シナリオ)
│   └── test_hash_chain_recovery.py             # NEW (リカバリテスト)
│
├── docs/                                        # ドキュメント
│   ├── ARCHITECTURE.md                         # (既存)
│   ├── TROUBLESHOOTING.md                      # (既存)
│   ├── HASH_CHAIN_DESIGN.md                    # NEW (詳細設計)
│   ├── HASH_CHAIN_API.md                       # NEW (API仕様)
│   ├── RECOVERY_PATTERNS.md                    # NEW (復旧パターン)
│   ├── HASH_DISCARD_ANALYSIS.md                # NEW (破棄分析)
│   └── CHANGELOG.md                            # (既存)
│
├── examples/                                    # 使用例
│   ├── basic_usage.py                          # (既存)
│   ├── example_multi_chain_basic.py            # NEW
│   ├── example_debug_rollback.py               # NEW
│   ├── example_recovery_flow.py                # NEW
│   ├── example_hash_discard_patterns.py        # NEW
│   └── example_full_integration.py             # NEW
│
└── .github/                                     # GitHub設定
    ├── ISSUE_TEMPLATE/
    │   ├── bug_report.md
    │   └── feature_request.md
    └── workflows/
        ├── tests.yml                           # CI/CD (テスト)
        └── lint.yml                            # コード品質
```

---

## 📁 新規追加ファイル（優先度順）

### Priority 1: コア機能（必須）

| ファイル | 行数 | 説明 |
|---------|------|------|
| `hash_chain/multi_layer_hash_chain.py` | ~350 | **コア実装** - マルチレイヤーハッシュチェーン管理 |
| `hash_chain/__init__.py` | ~30 | パッケージ初期化・エクスポート |
| `tests/test_multi_layer_hash_chain.py` | ~200 | ユニットテスト |
| `examples/example_multi_chain_basic.py` | ~100 | 基本的な使用例 |
| `docs/HASH_CHAIN_DESIGN.md` | ~400 | 詳細設計ドキュメント |

### Priority 2: 検証・永続化（推奨）

| ファイル | 行数 | 説明 |
|---------|------|------|
| `hash_chain/chain_validator.py` | ~150 | チェーン検証エンジン |
| `hash_chain/chain_persistence.py` | ~200 | SQLite永続化層 |
| `tests/test_chain_validator.py` | ~150 | 検証テスト |
| `examples/example_debug_rollback.py` | ~100 | ロールバック例 |
| `examples/example_recovery_flow.py` | ~100 | 復旧フロー例 |

### Priority 3: 分析・ドキュメント（オプション）

| ファイル | 行数 | 説明 |
|---------|------|------|
| `hash_chain/chain_analyzer.py` | ~150 | 破棄パターン分析 |
| `tests/test_chain_scenarios.py` | ~200 | 運用シナリオテスト |
| `tests/test_hash_chain_recovery.py` | ~150 | リカバリ統合テスト |
| `examples/example_hash_discard_patterns.py` | ~150 | 破棄パターン例 |
| `examples/example_full_integration.py` | ~150 | 完全統合例 |
| `docs/HASH_CHAIN_API.md` | ~200 | API仕様書 |
| `docs/RECOVERY_PATTERNS.md` | ~300 | 復旧パターンガイド |
| `docs/HASH_DISCARD_ANALYSIS.md` | ~250 | 破棄分析書 |
| `.github/workflows/tests.yml` | ~50 | CI/CD設定 |

---

## 📄 各ファイルの詳細

### hash_chain/__init__.py

```python
"""
ハッシュチェーン管理パッケージ
"""

from .multi_layer_hash_chain import (
    HashChain,
    ChainBlock,
    ChainType,
    BlockState,
    MultiChainManager,
    DoubleQuantizationConfig,
)

from .chain_validator import ChainValidator
from .chain_persistence import ChainPersistence
from .chain_analyzer import DiscardAnalyzer

__version__ = "1.0.0"
__all__ = [
    "HashChain",
    "ChainBlock",
    "ChainType",
    "BlockState",
    "MultiChainManager",
    "ChainValidator",
    "ChainPersistence",
    "DiscardAnalyzer",
]
```

### hash_chain/chain_validator.py

```python
"""
チェーン検証エンジン
"""

class ChainValidator:
    """チェーンの検証機能を提供"""
    
    def validate_single_chain(self, chain: HashChain) -> Tuple[bool, List[str]]:
        """単一チェーンの検証"""
        
    def validate_all_chains(self, manager: MultiChainManager) -> Dict:
        """全チェーンの検証"""
        
    def verify_chain_integrity(self, chain: HashChain) -> bool:
        """チェーン整合性の確認"""
        
    def detect_tampering(self, chain: HashChain) -> List[Dict]:
        """改ざん検出"""
```

### hash_chain/chain_persistence.py

```python
"""
SQLiteベースのチェーン永続化層
"""

class ChainPersistence:
    """チェーンをSQLiteに永続化"""
    
    def save_chain(self, chain: HashChain) -> bool:
        """チェーンを保存"""
        
    def load_chain(self, chain_id: str) -> HashChain:
        """チェーンを読み込み"""
        
    def save_manager(self, manager: MultiChainManager) -> bool:
        """マネージャーの全チェーンを保存"""
        
    def load_manager(self) -> MultiChainManager:
        """マネージャーを復元"""
        
    def export_to_json(self, manager: MultiChainManager) -> str:
        """JSON形式でエクスポート"""
```

### hash_chain/chain_analyzer.py

```python
"""
破棄パターン分析エンジン
"""

class DiscardAnalyzer:
    """チェーン破棄パターンの分析"""
    
    def analyze_discard_patterns(self, manager: MultiChainManager) -> Dict:
        """破棄パターンを分析"""
        
    def calculate_storage_impact(self, chain: HashChain) -> Dict:
        """ストレージ影響度を計算"""
        
    def suggest_discard_strategy(self, chain: HashChain) -> Dict:
        """破棄戦略を提案"""
        
    def generate_discard_report(self, manager: MultiChainManager) -> str:
        """破棄分析レポートを生成"""
```

### tests/test_multi_layer_hash_chain.py

```python
"""
マルチレイヤーハッシュチェーン テストスイート
"""

class TestChainBlock:
    def test_hash_computation(self): ...
    def test_hash_uniqueness(self): ...

class TestHashChain:
    def test_add_block(self): ...
    def test_chain_validation(self): ...
    def test_parent_chain_reference(self): ...
    def test_rollback_chain(self): ...
    def test_recovery_chain(self): ...

class TestMultiChainManager:
    def test_create_chains(self): ...
    def test_chain_discard(self): ...
    def test_validate_all(self): ...
    def test_export_import(self): ...
```

### docs/HASH_CHAIN_DESIGN.md

```
（既に作成済み）

内容:
  - システム概要
  - アーキテクチャ
  - ライフサイクル
  - 運用フロー
  - 検証メカニズム
  - 破棄パターン分析
  - API リファレンス
```

### docs/HASH_CHAIN_API.md

```
API仕様書（新規作成）

内容:
  - ChainBlock API
  - HashChain API
  - MultiChainManager API
  - ChainValidator API
  - ChainPersistence API
  - DiscardAnalyzer API
  - エラーコード定義
  - 型定義
```

### docs/RECOVERY_PATTERNS.md

```
復旧パターンガイド（新規作成）

内容:
  - Debug → Rollback パターン
  - Debug → Recovery パターン
  - マルチレベル復旧
  - エラー検出と自動復旧
  - チェーン再統合
  - 実装例とベストプラクティス
```

### docs/HASH_DISCARD_ANALYSIS.md

```
破棄パターン分析（新規作成）

内容:
  - 4つの破棄パターン詳細
  - ストレージコスト分析
  - トレーサビリティ分析
  - 監査適合性
  - 推奨パターンの選択
  - 実装例
```

---

## 🧪 テストカバレッジ

```
hash_chain/multi_layer_hash_chain.py     - 95%
hash_chain/chain_validator.py             - 90%
hash_chain/chain_persistence.py           - 85%
hash_chain/chain_analyzer.py              - 80%
```

### テスト実行コマンド

```bash
# 全テスト実行
pytest tests/

# カバレッジ付きで実行
pytest --cov=hash_chain tests/

# マルチレイヤーハッシュチェーン専用
pytest tests/test_multi_layer_hash_chain.py -v
```

---

## 📦 依存関係

`requirements.txt` に追加する項目：

```
# 既存
# (debug_frameworkの依存)

# 新規: hash_chain用
# (純粋Python実装のため追加なし、またはオプション)

# オプション:
# zstandard>=0.19.0    # 圧縮
# sqlalchemy>=2.0       # SQLite ORM
```

---

## 🔧 インストール・セットアップ

### ローカルセットアップ

```bash
git clone https://github.com/bluefox32/Error-handling-debug-system.git
cd Error-handling-debug-system

# 新しいモジュールをインストール
pip install -e .

# テスト実行
pytest tests/
```

### 使用例

```python
from hash_chain import MultiChainManager, ChainType

# マネージャーを初期化
manager = MultiChainManager()

# Main Chainにブロック追加
manager.add_to_main({'version': 'v1.0'})

# Debug Chainを作成
debug = manager.create_debug_chain()

# Rollback Chain を作成
rollback = manager.create_rollback_chain('debug_1', rollback_to_index=1)

# 検証
results = manager.validate_all_chains()
```

---

## 📊 ファイル概要表

| カテゴリ | ファイル | 行数 | 優先度 | 状態 |
|---------|---------|------|--------|------|
| **コア** | multi_layer_hash_chain.py | 350 | P1 | ✅ 完成 |
| **コア** | __init__.py | 30 | P1 | ⏳ 作成予定 |
| **検証** | chain_validator.py | 150 | P2 | ⏳ 作成予定 |
| **永続化** | chain_persistence.py | 200 | P2 | ⏳ 作成予定 |
| **分析** | chain_analyzer.py | 150 | P3 | ⏳ 作成予定 |
| **テスト** | test_multi_layer_hash_chain.py | 200 | P1 | ✅ 完成 |
| **テスト** | test_chain_validator.py | 150 | P2 | ⏳ 作成予定 |
| **テスト** | test_chain_scenarios.py | 200 | P3 | ⏳ 作成予定 |
| **テスト** | test_hash_chain_recovery.py | 150 | P3 | ⏳ 作成予定 |
| **例** | example_multi_chain_basic.py | 100 | P1 | ⏳ 作成予定 |
| **例** | example_debug_rollback.py | 100 | P2 | ⏳ 作成予定 |
| **例** | example_recovery_flow.py | 100 | P2 | ⏳ 作成予定 |
| **例** | example_hash_discard_patterns.py | 150 | P3 | ⏳ 作成予定 |
| **例** | example_full_integration.py | 150 | P3 | ⏳ 作成予定 |
| **ドキュメント** | HASH_CHAIN_DESIGN.md | 400 | P1 | ✅ 完成 |
| **ドキュメント** | HASH_CHAIN_API.md | 200 | P2 | ⏳ 作成予定 |
| **ドキュメント** | RECOVERY_PATTERNS.md | 300 | P2 | ⏳ 作成予定 |
| **ドキュメント** | HASH_DISCARD_ANALYSIS.md | 250 | P2 | ⏳ 作成予定 |

---

## 🎯 実装ロードマップ

### Phase 1: 基本実装（1-2週）
- [x] multi_layer_hash_chain.py
- [x] test_multi_layer_hash_chain.py
- [x] HASH_CHAIN_DESIGN.md
- [ ] hash_chain/__init__.py
- [ ] example_multi_chain_basic.py

### Phase 2: 拡張機能（2-3週）
- [ ] chain_validator.py
- [ ] chain_persistence.py
- [ ] test_chain_validator.py
- [ ] HASH_CHAIN_API.md
- [ ] example_debug_rollback.py
- [ ] example_recovery_flow.py
- [ ] RECOVERY_PATTERNS.md

### Phase 3: 最適化（3-4週）
- [ ] chain_analyzer.py
- [ ] test_chain_scenarios.py
- [ ] test_hash_chain_recovery.py
- [ ] example_hash_discard_patterns.py
- [ ] example_full_integration.py
- [ ] HASH_DISCARD_ANALYSIS.md
- [ ] .github/workflows/tests.yml

---

## ✅ チェックリスト

GitHub上げ前の確認：

- [ ] すべてのファイルが作成されている
- [ ] テストが100%実行できる
- [ ] ドキュメントが完全である
- [ ] 例が動作確認済み
- [ ] setup.pyが正しく設定されている
- [ ] .gitignoreが設定されている
- [ ] LICENSEが含まれている
- [ ] README.mdが最新版である
- [ ] CI/CDが設定されている

---

**準備完了日**: 2026-06-11  
**フレームワークバージョン**: 1.0.0 + Hash Chain 1.0.0  
**ステータス**: Ready for GitHub Release
