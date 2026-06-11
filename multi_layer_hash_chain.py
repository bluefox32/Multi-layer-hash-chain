#!/usr/bin/env python3
"""
多層ハッシュチェーン管理システム
デバッグ用・ロールバック用・復旧用の3パターンを独立した不変チェーンで管理

アーキテクチャ:
  Main Chain (本番チェーン)
    ↓
  Debug Chain (デバッグチェーン：新規ハッシュ検証)
    ├─ Rollback Chain (ロールバック用：デバッグ→新規)
    └─ Recovery Chain (復旧用：デバッグ→新規)

各チェーンの特性:
  - 不変チェーン（tamper-proof）
  - 親チェーンのハッシュを参照
  - 独立したハッシュ系列
  - 破棄・統合・検証可能
"""

import hashlib
import json
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime


class ChainType(Enum):
    """チェーンの種類"""
    MAIN = "main"           # 本番チェーン
    DEBUG = "debug"         # デバッグチェーン
    ROLLBACK = "rollback"   # ロールバック復旧
    RECOVERY = "recovery"   # 通常復旧


class BlockState(Enum):
    """ブロックの状態"""
    VALID = "valid"         # 検証済み・正常
    PENDING = "pending"     # 検証中
    INVALID = "invalid"     # 無効・エラー
    ROLLED_BACK = "rolled_back"  # ロールバック済み
    RECOVERED = "recovered" # 復旧済み
    DISCARDED = "discarded" # 破棄済み


@dataclass
class ChainBlock:
    """ハッシュチェーンのブロック"""
    index: int                    # ブロック番号
    timestamp: str                # タイムスタンプ
    data: Dict                    # ペイロードデータ
    previous_hash: str            # 前ブロックのハッシュ
    parent_chain_hash: Optional[str] = None  # 親チェーンのハッシュ（分岐時）
    chain_type: str = "main"      # チェーンの種類
    state: str = "pending"        # ブロック状態
    hash: str = ""                # このブロックのハッシュ
    
    def compute_hash(self) -> str:
        """ブロックのハッシュを計算"""
        block_data = {
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash,
            'parent_chain_hash': self.parent_chain_hash,
            'chain_type': self.chain_type,
        }
        block_json = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_json.encode()).hexdigest()


class HashChain:
    """不変ハッシュチェーン"""
    
    def __init__(self, chain_type: ChainType, parent_chain: Optional['HashChain'] = None):
        self.chain_type = chain_type
        self.parent_chain = parent_chain
        self.blocks: List[ChainBlock] = []
        self.metadata = {
            'created_at': datetime.utcnow().isoformat(),
            'parent_chain_type': parent_chain.chain_type.value if parent_chain else None,
            'parent_chain_hash': self._get_parent_chain_hash(),
            'branch_point_index': None,
        }
    
    def _get_parent_chain_hash(self) -> Optional[str]:
        """親チェーンの最後のブロックハッシュを取得"""
        if self.parent_chain and self.parent_chain.blocks:
            return self.parent_chain.blocks[-1].hash
        return None
    
    def add_block(self, data: Dict) -> ChainBlock:
        """新しいブロックを追加"""
        index = len(self.blocks)
        timestamp = datetime.utcnow().isoformat()
        
        # 前ブロックのハッシュを取得
        previous_hash = self.blocks[-1].hash if self.blocks else "0" * 64
        
        # 新規ブロックを作成
        block = ChainBlock(
            index=index,
            timestamp=timestamp,
            data=data,
            previous_hash=previous_hash,
            parent_chain_hash=self._get_parent_chain_hash() if index == 0 else None,
            chain_type=self.chain_type.value,
            state=BlockState.PENDING.value,
        )
        
        # ハッシュを計算
        block.hash = block.compute_hash()
        
        # チェーンに追加
        self.blocks.append(block)
        
        return block
    
    def validate_chain(self) -> Tuple[bool, List[str]]:
        """チェーン全体を検証"""
        errors = []
        
        if not self.blocks:
            return True, []
        
        # 親チェーンとの検証
        if self.parent_chain:
            if not self.blocks[0].parent_chain_hash:
                errors.append("分岐ポイントのhash参照がない")
            elif self.blocks[0].parent_chain_hash != self._get_parent_chain_hash():
                errors.append(f"親チェーン参照が一致しない")
        
        # 各ブロックの連続性を検証
        for i, block in enumerate(self.blocks):
            if i == 0:
                # 最初のブロック
                if block.previous_hash != "0" * 64 and self.parent_chain is None:
                    errors.append(f"Block 0: 親がないのに前hash参照がある")
            else:
                # 後続ブロック
                if block.previous_hash != self.blocks[i-1].hash:
                    errors.append(f"Block {i}: 前ブロックのhashが一致しない")
            
            # ハッシュの再計算
            computed_hash = block.compute_hash()
            if computed_hash != block.hash:
                errors.append(f"Block {i}: ハッシュが改ざんされている")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def get_chain_hash(self) -> str:
        """チェーン全体のハッシュを取得（最後のブロックハッシュ）"""
        if not self.blocks:
            return hashlib.sha256(b"empty").hexdigest()
        return self.blocks[-1].hash
    
    def rollback_to(self, index: int) -> 'HashChain':
        """指定インデックスまでロールバック"""
        if index >= len(self.blocks):
            raise ValueError("インデックスが範囲外")
        
        # ロールバック状態のチェーンを新規作成
        rollback_chain = HashChain(ChainType.ROLLBACK, parent_chain=self)
        
        # ロールバック対象のデータを追加
        for i in range(index + 1):
            original_block = self.blocks[i]
            rollback_chain.add_block({
                'original_index': i,
                'data': original_block.data,
                'action': 'rollback',
            })
        
        return rollback_chain
    
    def create_recovery_chain(self, from_index: int = 0) -> 'HashChain':
        """復旧用の新規チェーンを作成"""
        recovery_chain = HashChain(ChainType.RECOVERY, parent_chain=self)
        
        # 復旧対象のデータを追加
        for i in range(from_index, len(self.blocks)):
            original_block = self.blocks[i]
            recovery_chain.add_block({
                'original_index': i,
                'data': original_block.data,
                'action': 'recovery',
            })
        
        return recovery_chain
    
    def discard(self) -> Dict:
        """チェーンを破棄（メタデータのみ保持）"""
        discarded_info = {
            'chain_type': self.chain_type.value,
            'blocks_count': len(self.blocks),
            'chain_hash': self.get_chain_hash(),
            'discarded_at': datetime.utcnow().isoformat(),
            'parent_chain': self.metadata['parent_chain_type'],
            'parent_chain_hash': self.metadata['parent_chain_hash'],
        }
        
        # ブロックを削除
        self.blocks = []
        
        return discarded_info


class MultiChainManager:
    """複数チェーンの統合管理"""
    
    def __init__(self):
        self.chains: Dict[str, HashChain] = {}
        self.chain_graph: Dict[str, List[str]] = {}  # チェーン間の依存関係
        self.discarded_chains: List[Dict] = []
        
        # Main チェーンを初期化
        self.main_chain = HashChain(ChainType.MAIN)
        self.chains['main'] = self.main_chain
        self.chain_graph['main'] = []
    
    def add_to_main(self, data: Dict) -> ChainBlock:
        """Main チェーンにブロック追加"""
        block = self.main_chain.add_block(data)
        block.state = BlockState.VALID.value
        return block
    
    def create_debug_chain(self) -> HashChain:
        """デバッグ用チェーンを作成"""
        debug_chain = HashChain(ChainType.DEBUG, parent_chain=self.main_chain)
        
        chain_id = f"debug_{len(self.chains)}"
        self.chains[chain_id] = debug_chain
        self.chain_graph['main'].append(chain_id)
        
        return debug_chain
    
    def create_rollback_chain(self, debug_chain_id: str, rollback_to_index: int) -> HashChain:
        """ロールバック用チェーンを作成"""
        if debug_chain_id not in self.chains:
            raise ValueError(f"チェーン {debug_chain_id} が見つかりません")
        
        debug_chain = self.chains[debug_chain_id]
        rollback_chain = debug_chain.rollback_to(rollback_to_index)
        
        chain_id = f"rollback_{len(self.chains)}"
        self.chains[chain_id] = rollback_chain
        self.chain_graph[debug_chain_id] = self.chain_graph.get(debug_chain_id, []) + [chain_id]
        
        return rollback_chain
    
    def create_recovery_chain(self, debug_chain_id: str, from_index: int = 0) -> HashChain:
        """復旧用チェーンを作成"""
        if debug_chain_id not in self.chains:
            raise ValueError(f"チェーン {debug_chain_id} が見つかりません")
        
        debug_chain = self.chains[debug_chain_id]
        recovery_chain = debug_chain.create_recovery_chain(from_index)
        
        chain_id = f"recovery_{len(self.chains)}"
        self.chains[chain_id] = recovery_chain
        self.chain_graph[debug_chain_id] = self.chain_graph.get(debug_chain_id, []) + [chain_id]
        
        return recovery_chain
    
    def validate_all_chains(self) -> Dict[str, Tuple[bool, List[str]]]:
        """全チェーンを検証"""
        results = {}
        for chain_id, chain in self.chains.items():
            is_valid, errors = chain.validate_chain()
            results[chain_id] = (is_valid, errors)
        return results
    
    def discard_chain(self, chain_id: str) -> Dict:
        """チェーンを破棄"""
        if chain_id not in self.chains:
            raise ValueError(f"チェーン {chain_id} が見つかりません")
        
        if chain_id == 'main':
            raise ValueError("Main チェーンは破棄できません")
        
        chain = self.chains[chain_id]
        discarded_info = chain.discard()
        
        self.discarded_chains.append(discarded_info)
        del self.chains[chain_id]
        
        return discarded_info
    
    def get_chain_stats(self) -> Dict:
        """チェーン統計を取得"""
        stats = {
            'active_chains': len(self.chains),
            'discarded_chains': len(self.discarded_chains),
            'chain_details': {},
        }
        
        for chain_id, chain in self.chains.items():
            stats['chain_details'][chain_id] = {
                'type': chain.chain_type.value,
                'blocks': len(chain.blocks),
                'chain_hash': chain.get_chain_hash()[:16],  # 先頭16文字
                'parent': chain.metadata['parent_chain_type'],
            }
        
        return stats
    
    def export_chains(self) -> Dict:
        """すべてのチェーンをエクスポート"""
        export_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'active_chains': {},
            'discarded_chains': self.discarded_chains,
            'chain_graph': self.chain_graph,
        }
        
        for chain_id, chain in self.chains.items():
            export_data['active_chains'][chain_id] = {
                'metadata': chain.metadata,
                'blocks': [asdict(block) for block in chain.blocks],
            }
        
        return export_data


# ============================================================================
# テストと実例
# ============================================================================

def test_multi_chain_system():
    """複数チェーンシステムのテスト"""
    print("\n" + "="*80)
    print("マルチレイヤーハッシュチェーン管理システム テスト")
    print("="*80)
    
    manager = MultiChainManager()
    
    # Step 1: Main チェーンにブロック追加
    print("\n[1] Main チェーンに本番データを追加")
    for i in range(3):
        block = manager.add_to_main({'version': f'v1.{i}', 'status': 'production'})
        print(f"  Block {i}: {block.hash[:16]}...")
    
    main_chain_hash = manager.main_chain.get_chain_hash()
    print(f"Main Chain Hash: {main_chain_hash[:16]}...")
    
    # Step 2: デバッグチェーン作成
    print("\n[2] デバッグチェーンを作成（新規ハッシュ検証）")
    debug_chain = manager.create_debug_chain()
    debug_chain_id = f"debug_{len(manager.chains) - 1}"
    
    for i in range(2):
        block = debug_chain.add_block({'version': f'v2.{i}', 'status': 'debug', 'test_id': f'test_{i}'})
        print(f"  Block {i}: {block.hash[:16]}...")
    
    debug_chain_hash = debug_chain.get_chain_hash()
    print(f"Debug Chain Hash: {debug_chain_hash[:16]}...")
    
    # Step 3: ロールバック用チェーン作成
    print("\n[3] ロールバック用チェーンを作成（デバッグ→新規チェーン繋ぎ）")
    rollback_chain = manager.create_rollback_chain(debug_chain_id, rollback_to_index=0)
    rollback_chain_id = f"rollback_{len(manager.chains) - 1}"
    
    for block in rollback_chain.blocks:
        print(f"  Block {block.index}: {block.hash[:16]}... (state: {block.state})")
    
    rollback_chain_hash = rollback_chain.get_chain_hash()
    print(f"Rollback Chain Hash: {rollback_chain_hash[:16]}...")
    
    # Step 4: 復旧用チェーン作成
    print("\n[4] 復旧用チェーンを作成（デバッグ→新規チェーン繋ぎ）")
    recovery_chain = manager.create_recovery_chain(debug_chain_id, from_index=1)
    recovery_chain_id = f"recovery_{len(manager.chains) - 1}"
    
    for block in recovery_chain.blocks:
        print(f"  Block {block.index}: {block.hash[:16]}... (state: {block.state})")
    
    recovery_chain_hash = recovery_chain.get_chain_hash()
    print(f"Recovery Chain Hash: {recovery_chain_hash[:16]}...")
    
    # Step 5: チェーン検証
    print("\n[5] 全チェーンの検証")
    validation_results = manager.validate_all_chains()
    for chain_id, (is_valid, errors) in validation_results.items():
        status = "✓ VALID" if is_valid else "✗ INVALID"
        print(f"  {chain_id:20} {status}")
        if errors:
            for error in errors:
                print(f"    - {error}")
    
    # Step 6: チェーンの破棄
    print("\n[6] 不要なデバッグチェーンを破棄")
    discarded = manager.discard_chain(debug_chain_id)
    print(f"  破棄されたチェーン: {discarded['chain_type']}")
    print(f"  元のブロック数: {discarded['blocks_count']}")
    print(f"  チェーンハッシュ: {discarded['chain_hash'][:16]}...")
    
    # Step 7: 統計情報
    print("\n[7] チェーン統計")
    stats = manager.get_chain_stats()
    print(f"  アクティブチェーン: {stats['active_chains']}")
    print(f"  破棄済みチェーン: {stats['discarded_chains']}")
    print(f"\n  チェーン詳細:")
    for chain_id, details in stats['chain_details'].items():
        print(f"    {chain_id:20} type={details['type']:10} blocks={details['blocks']} parent={details['parent']}")
    
    # Step 8: チェーングラフ
    print("\n[8] チェーン依存グラフ")
    for parent, children in manager.chain_graph.items():
        if children:
            print(f"  {parent}")
            for child in children:
                print(f"    └─ {child}")
        else:
            print(f"  {parent} (リーフノード)")
    
    # Step 9: エクスポート
    print("\n[9] チェーンデータエクスポート")
    export_data = manager.export_chains()
    print(f"  タイムスタンプ: {export_data['timestamp']}")
    print(f"  アクティブチェーン数: {len(export_data['active_chains'])}")
    print(f"  破棄済みチェーン数: {len(export_data['discarded_chains'])}")
    
    return manager, export_data


if __name__ == "__main__":
    manager, export_data = test_multi_chain_system()
    
    # JSON出力
    print("\n" + "="*80)
    print("エクスポートデータ（JSON形式）")
    print("="*80)
    print(json.dumps(export_data, indent=2, default=str)[:500] + "...")
