#!/usr/bin/env python3
"""
RICK System Blueprint Generator
Automatically creates visual architecture diagram with color-coded nodes
Generates PNG files showing system structure, file relationships, and status

Usage:
    python3 scripts/generate_blueprint.py
    python3 scripts/generate_blueprint.py --trigger ML_INTEGRATION --output custom_name.png
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple
import argparse

# Try to import graphviz, fallback to manual install prompt
try:
    import graphviz
except ImportError:
    print("❌ graphviz module not found. Install with:")
    print("   pip install graphviz")
    print("   sudo apt-get install graphviz  # On Debian/Ubuntu")
    exit(1)

class RickBlueprintGenerator:
    """Generates visual system architecture blueprints"""
    
    # Color scheme (cyberpunk/matrix aesthetic)
    COLORS = {
        'background': '#0a0e27',
        'active': '#00ff41',      # Green - operational modules
        'critical': '#ff4444',    # Red - safety systems
        'testing': '#ffff00',     # Yellow - in development
        'inactive': '#404040',    # Gray - legacy/dead code
        'connection': '#00d4ff',  # Cyan - data flow
        'text': '#ffffff'         # White - labels
    }
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path('/home/ing/RICK/R_H_UNI')
        self.blueprints_dir = self.project_root / 'blueprints'
        self.current_dir = self.blueprints_dir / 'current'
        self.archive_dir = self.blueprints_dir / 'archive'
        self.metadata_dir = self.blueprints_dir / 'metadata'
        
        # Ensure directories exist
        for d in [self.blueprints_dir, self.current_dir, self.archive_dir, self.metadata_dir]:
            d.mkdir(parents=True, exist_ok=True)
    
    def scan_codebase(self) -> Dict:
        """Scan project to gather node information"""
        nodes = {}
        
        # Foundation layer
        foundation_files = list((self.project_root / 'foundation').glob('*.py')) if (self.project_root / 'foundation').exists() else []
        nodes['foundation'] = {
            'name': 'FOUNDATION',
            'files': [f.name for f in foundation_files[:5]],
            'description': 'Enforces PIN 841921 and immutable trading rules',
            'size': self._get_dir_size(self.project_root / 'foundation'),
            'status': 'active',
            'color': self.COLORS['critical'],  # Critical safety
            'dependencies': []
        }
        
        # Brokers layer
        broker_files = list((self.project_root / 'brokers').glob('*.py')) if (self.project_root / 'brokers').exists() else []
        nodes['brokers'] = {
            'name': 'BROKERS',
            'files': [f.name for f in broker_files[:5]],
            'description': 'Connects to OANDA FX and Coinbase crypto APIs',
            'size': self._get_dir_size(self.project_root / 'brokers'),
            'status': 'active',
            'color': self.COLORS['active'],
            'dependencies': ['foundation']
        }
        
        # ML Learning layer
        ml_files = list((self.project_root / 'ml_learning').glob('*.py')) if (self.project_root / 'ml_learning').exists() else []
        # Check if integrated (look for imports in ghost engine)
        ml_integrated = self._check_ml_integration()
        nodes['ml_learning'] = {
            'name': 'ML MODELS',
            'files': [f.name for f in ml_files[:5]],
            'description': 'Three ML models (A/B/C) for Forex, Crypto, Futures',
            'size': self._get_dir_size(self.project_root / 'ml_learning'),
            'status': 'active' if ml_integrated else 'testing',
            'color': self.COLORS['active'] if ml_integrated else self.COLORS['testing'],
            'dependencies': ['foundation']
        }
        
        # Risk management layer
        risk_files = list((self.project_root / 'risk').glob('*.py')) if (self.project_root / 'risk').exists() else []
        nodes['risk'] = {
            'name': 'RISK MANAGEMENT',
            'files': [f.name for f in risk_files[:5]],
            'description': 'Session breaker (-5% halt), OCO validator, risk control',
            'size': self._get_dir_size(self.project_root / 'risk'),
            'status': 'active',
            'color': self.COLORS['critical'],
            'dependencies': ['foundation']
        }
        
        # Wolf packs (strategies)
        wolf_files = list((self.project_root / 'wolf_packs').glob('*.py')) if (self.project_root / 'wolf_packs').exists() else []
        nodes['wolf_packs'] = {
            'name': 'STRATEGIES',
            'files': [f.name for f in wolf_files[:5]],
            'description': 'Trading strategies with stochastic config loading',
            'size': self._get_dir_size(self.project_root / 'wolf_packs'),
            'status': 'active',
            'color': self.COLORS['active'],
            'dependencies': ['foundation', 'ml_learning']
        }
        
        # Ghost engine
        ghost_running = self._check_ghost_running()
        nodes['ghost_engine'] = {
            'name': 'GHOST ENGINE',
            'files': ['live_ghost_engine.py'],
            'description': 'Real-time market scanner with 750ms polling (no real trades)',
            'size': self._get_file_size(self.project_root / 'RICK_LIVE_DEPLOYMENT' / 'live_ghost_engine.py'),
            'status': 'active' if ghost_running else 'inactive',
            'color': self.COLORS['active'] if ghost_running else self.COLORS['inactive'],
            'dependencies': ['foundation', 'brokers', 'risk', 'wolf_packs']
        }
        
        return nodes
    
    def _get_dir_size(self, path: Path) -> str:
        """Get directory size in human-readable format"""
        if not path.exists():
            return '0 KB'
        
        try:
            result = subprocess.run(['du', '-sh', str(path)], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.split()[0]
        except:
            pass
        return 'Unknown'
    
    def _get_file_size(self, path: Path) -> str:
        """Get file size in human-readable format"""
        if not path.exists():
            return '0 KB'
        
        size = path.stat().st_size
        for unit in ['B', 'KB', 'MB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} GB"
    
    def _check_ml_integration(self) -> bool:
        """Check if ML models are integrated into ghost engine"""
        ghost_engine = self.project_root / 'RICK_LIVE_DEPLOYMENT' / 'live_ghost_engine.py'
        if not ghost_engine.exists():
            return False
        
        try:
            content = ghost_engine.read_text()
            return 'ml_learning' in content or 'MLModel' in content
        except:
            return False
    
    def _check_ghost_running(self) -> bool:
        """Check if ghost engine is currently running"""
        try:
            result = subprocess.run(['pgrep', '-f', 'live_ghost_engine'], capture_output=True, timeout=2)
            return result.returncode == 0
        except:
            return False
    
    def _get_git_info(self) -> Tuple[str, str]:
        """Get current git branch and commit hash"""
        try:
            branch_result = subprocess.run(['git', 'branch', '--show-current'], 
                                          cwd=self.project_root, 
                                          capture_output=True, 
                                          text=True, 
                                          timeout=2)
            branch = branch_result.stdout.strip() if branch_result.returncode == 0 else 'unknown'
            
            commit_result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'],
                                          cwd=self.project_root,
                                          capture_output=True,
                                          text=True,
                                          timeout=2)
            commit = commit_result.stdout.strip() if commit_result.returncode == 0 else 'unknown'
            
            return branch, commit
        except:
            return 'unknown', 'unknown'
    
    def generate(self, trigger: str = 'MANUAL', output_name: str = None) -> Path:
        """Generate blueprint PNG file"""
        
        # Scan codebase
        nodes = self.scan_codebase()
        
        # Get git info
        branch, commit = self._get_git_info()
        
        # Count stats
        active_count = sum(1 for n in nodes.values() if n['status'] == 'active')
        testing_count = sum(1 for n in nodes.values() if n['status'] == 'testing')
        inactive_count = sum(1 for n in nodes.values() if n['status'] == 'inactive')
        
        # Create graphviz diagram
        dot = graphviz.Digraph(
            'RICK_Blueprint',
            comment='RBOTzilla UNI System Architecture',
            format='png',
            engine='dot'
        )
        
        # Graph styling
        dot.attr(
            bgcolor=self.COLORS['background'],
            fontname='Courier New Bold',
            fontsize='14',
            fontcolor=self.COLORS['text'],
            rankdir='TB',  # Top to bottom
            splines='ortho',  # Orthogonal edges
            nodesep='0.8',
            ranksep='1.2'
        )
        
        # Edge styling
        dot.attr(
            'edge',
            color=self.COLORS['connection'],
            fontcolor=self.COLORS['text'],
            fontsize='10',
            fontname='Courier New',
            penwidth='2'
        )
        
        # Node styling (default)
        dot.attr(
            'node',
            shape='box',
            style='filled,rounded',
            fontname='Courier New Bold',
            fontsize='11',
            margin='0.3,0.2'
        )
        
        # Add header
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
        header = (
            f'RICK (RBOTzilla UNI) System Blueprint\\n'
            f'Generated: {timestamp} | Trigger: {trigger}\\n'
            f'Branch: {branch} | Commit: {commit}\\n'
            f'Status: {active_count} Active, {testing_count} Testing, {inactive_count} Inactive'
        )
        dot.attr(label=header, labelloc='t', fontsize='12')
        
        # Add nodes
        for node_id, node_data in nodes.items():
            # Build node label
            files_str = '\\n'.join([f'• {f}' for f in node_data['files'][:3]])
            if len(node_data['files']) > 3:
                files_str += f'\\n  + {len(node_data["files"]) - 3} more...'
            
            status_icon = {
                'active': '✅',
                'testing': '🟡',
                'inactive': '⚫',
                'critical': '🔴'
            }.get(node_data['status'], '❓')
            
            label = (
                f'{node_data["name"]}\\n'
                f'{"─" * 25}\\n'
                f'Files:\\n{files_str}\\n\\n'
                f'{node_data["description"]}\\n\\n'
                f'Size: {node_data["size"]} | {status_icon} {node_data["status"].upper()}'
            )
            
            dot.node(
                node_id,
                label,
                fillcolor=node_data['color'],
                fontcolor='black' if node_data['color'] in [self.COLORS['active'], self.COLORS['testing']] else self.COLORS['text']
            )
        
        # Add edges (data flow)
        edges = [
            ('foundation', 'brokers', 'Charter\\nValidation'),
            ('foundation', 'risk', 'Rules\\nEnforcement'),
            ('foundation', 'ml_learning', 'PIN\\nGate'),
            ('brokers', 'ghost_engine', 'Market\\nPricing'),
            ('ml_learning', 'wolf_packs', 'ML\\nSignals'),
            ('wolf_packs', 'ghost_engine', 'Trading\\nSignals'),
            ('risk', 'ghost_engine', 'Risk\\nChecks'),
            ('ghost_engine', 'risk', 'Trade\\nEvents'),
        ]
        
        for src, dst, label in edges:
            if src in nodes and dst in nodes:
                dot.edge(src, dst, label)
        
        # Add legend
        with dot.subgraph(name='cluster_legend') as legend:
            legend.attr(label='Legend', fontsize='10', style='filled', fillcolor='#1a1e37')
            legend.attr('node', shape='box', style='filled')
            
            legend.node('legend_active', '✅ Active/Operational', fillcolor=self.COLORS['active'], fontcolor='black')
            legend.node('legend_critical', '🔴 Critical/Safety', fillcolor=self.COLORS['critical'], fontcolor='black')
            legend.node('legend_testing', '🟡 In Development', fillcolor=self.COLORS['testing'], fontcolor='black')
            legend.node('legend_inactive', '⚫ Inactive/Legacy', fillcolor=self.COLORS['inactive'], fontcolor=self.COLORS['text'])
        
        # Generate filename
        timestamp_file = datetime.now().strftime('%Y%m%d_%H%M%S')
        if output_name:
            filename = output_name if output_name.endswith('.png') else f'{output_name}.png'
        else:
            filename = f'RICK_Blueprint_{trigger}_{timestamp_file}'
        
        output_path = self.archive_dir / filename
        
        # Render
        try:
            dot.render(str(output_path.with_suffix('')), cleanup=True)
            final_path = output_path.with_suffix('.png')
            
            # Create symlink to latest
            latest_link = self.current_dir / 'RICK_Blueprint_Latest.png'
            if latest_link.exists() or latest_link.is_symlink():
                latest_link.unlink()
            latest_link.symlink_to(final_path)
            
            # Update metadata
            self._update_metadata(final_path, trigger, nodes, branch, commit)
            
            print(f"✅ Blueprint generated successfully!")
            print(f"   📁 {final_path}")
            print(f"   🔗 {latest_link} (symlink)")
            
            return final_path
            
        except Exception as e:
            print(f"❌ Failed to generate blueprint: {e}")
            return None
    
    def _update_metadata(self, filepath: Path, trigger: str, nodes: Dict, branch: str, commit: str):
        """Update blueprint metadata index"""
        metadata_file = self.metadata_dir / 'blueprint_index.json'
        
        # Load existing metadata
        if metadata_file.exists():
            try:
                metadata = json.loads(metadata_file.read_text())
            except:
                metadata = {'blueprints': []}
        else:
            metadata = {'blueprints': []}
        
        # Add new entry
        entry = {
            'filename': filepath.name,
            'path': str(filepath),
            'generated': datetime.now(timezone.utc).isoformat(),
            'trigger': trigger,
            'git_branch': branch,
            'git_commit': commit,
            'total_nodes': len(nodes),
            'active_nodes': sum(1 for n in nodes.values() if n['status'] == 'active'),
            'testing_nodes': sum(1 for n in nodes.values() if n['status'] == 'testing'),
            'inactive_nodes': sum(1 for n in nodes.values() if n['status'] == 'inactive'),
            'nodes': {k: {'name': v['name'], 'status': v['status'], 'size': v['size']} for k, v in nodes.items()}
        }
        
        metadata['blueprints'].append(entry)
        
        # Save
        metadata_file.write_text(json.dumps(metadata, indent=2))
        print(f"   📊 Metadata updated: {metadata_file}")

def main():
    parser = argparse.ArgumentParser(description='Generate RICK system architecture blueprint')
    parser.add_argument('--trigger', default='MANUAL', help='Event that triggered generation')
    parser.add_argument('--output', help='Custom output filename')
    parser.add_argument('--project-root', help='Project root directory', default='/home/ing/RICK/R_H_UNI')
    
    args = parser.parse_args()
    
    generator = RickBlueprintGenerator(Path(args.project_root))
    generator.generate(trigger=args.trigger, output_name=args.output)

if __name__ == '__main__':
    main()
