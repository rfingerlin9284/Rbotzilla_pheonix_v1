#!/usr/bin/env python3
"""
GOLDEN AGE SIMULATION COMPARISON TEST
======================================
Compares original vs enhanced Golden Age simulation results

This script:
1. Runs both simulations
2. Compares performance metrics
3. Analyzes differences
4. Generates comparison report
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GoldenAgeComparator:
    """Compare original vs enhanced Golden Age simulations"""

    def __init__(self):
        self.original_report = None
        self.enhanced_report = None
        self.comparison = {}

    def load_report(self, report_path: str, report_type: str) -> bool:
        """Load simulation report from JSON file"""
        try:
            path = Path(report_path)
            if not path.exists():
                logger.error(f"{report_type} report not found: {report_path}")
                return False

            with open(path, 'r') as f:
                data = json.load(f)

            if report_type == 'original':
                self.original_report = data
            else:
                self.enhanced_report = data

            logger.info(f"✅ Loaded {report_type} report: {report_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load {report_type} report: {e}")
            return False

    def compare_metrics(self):
        """Compare key metrics between simulations"""
        if not self.original_report or not self.enhanced_report:
            logger.error("Both reports must be loaded before comparison")
            return

        orig = self.original_report.get('simulation_summary', {})
        enh = self.enhanced_report.get('simulation_summary', {})

        self.comparison = {
            'timestamp': datetime.now().isoformat(),
            'initial_capital': {
                'original': orig.get('initial_capital', 0),
                'enhanced': enh.get('initial_capital', 0),
                'difference': 0
            },
            'final_capital': {
                'original': orig.get('final_capital', 0),
                'enhanced': enh.get('final_capital', 0),
                'difference': enh.get('final_capital', 0) - orig.get('final_capital', 0),
                'improvement_pct': self._calc_improvement_pct(
                    orig.get('final_capital', 0),
                    enh.get('final_capital', 0)
                )
            },
            'total_deposited': {
                'original': orig.get('total_deposited', 0),
                'enhanced': enh.get('total_deposited', 0),
                'difference': enh.get('total_deposited', 0) - orig.get('total_deposited', 0)
            },
            'total_withdrawn': {
                'original': orig.get('total_withdrawn', 0),
                'enhanced': enh.get('total_withdrawn', 0),
                'difference': enh.get('total_withdrawn', 0) - orig.get('total_withdrawn', 0),
                'improvement_pct': self._calc_improvement_pct(
                    orig.get('total_withdrawn', 0),
                    enh.get('total_withdrawn', 0)
                )
            },
            'final_net_worth': {
                'original': orig.get('final_net_worth', 0),
                'enhanced': enh.get('final_net_worth', 0),
                'difference': enh.get('final_net_worth', 0) - orig.get('final_net_worth', 0),
                'improvement_pct': self._calc_improvement_pct(
                    orig.get('final_net_worth', 0),
                    enh.get('final_net_worth', 0)
                )
            },
            'total_pnl': {
                'original': orig.get('total_pnl', 0),
                'enhanced': enh.get('total_pnl', 0),
                'difference': enh.get('total_pnl', 0) - orig.get('total_pnl', 0),
                'improvement_pct': self._calc_improvement_pct(
                    orig.get('total_pnl', 0),
                    enh.get('total_pnl', 0)
                )
            },
            'roi': {
                'original': orig.get('roi_pct', 0),
                'enhanced': enh.get('roi_pct', 0),
                'difference': enh.get('roi_pct', 0) - orig.get('roi_pct', 0),
                'improvement_pct': self._calc_improvement_pct(
                    orig.get('roi_pct', 0),
                    enh.get('roi_pct', 0)
                )
            },
            'total_trades': {
                'original': orig.get('total_trades', 0),
                'enhanced': enh.get('total_trades', 0),
                'difference': enh.get('total_trades', 0) - orig.get('total_trades', 0)
            },
            'win_rate': {
                'original': orig.get('overall_win_rate', 0),
                'enhanced': enh.get('overall_win_rate', 0),
                'difference': enh.get('overall_win_rate', 0) - orig.get('overall_win_rate', 0)
            }
        }

        logger.info("✅ Metrics comparison complete")

    def _calc_improvement_pct(self, original: float, enhanced: float) -> float:
        """Calculate percentage improvement"""
        if original == 0:
            return 0.0
        return ((enhanced - original) / abs(original)) * 100

    def generate_report(self) -> str:
        """Generate comprehensive comparison report"""
        if not self.comparison:
            return "❌ No comparison data available"

        report_lines = [
            "=" * 100,
            "🏆 GOLDEN AGE SIMULATION COMPARISON REPORT",
            "=" * 100,
            "",
            "📊 PERFORMANCE METRICS",
            "-" * 100,
            ""
        ]

        # Helper function to format currency
        def fmt_curr(value):
            return f"${value:,.2f}"

        def fmt_pct(value):
            return f"{value:,.2f}%"

        # Final Capital
        fc = self.comparison['final_capital']
        report_lines.extend([
            "💰 FINAL CAPITAL:",
            f"   Original:     {fmt_curr(fc['original'])}",
            f"   Enhanced:     {fmt_curr(fc['enhanced'])}",
            f"   Difference:   {fmt_curr(fc['difference'])} ({fmt_pct(fc['improvement_pct'])} improvement)",
            ""
        ])

        # Final Net Worth
        fnw = self.comparison['final_net_worth']
        report_lines.extend([
            "💎 FINAL NET WORTH (Capital + Withdrawn):",
            f"   Original:     {fmt_curr(fnw['original'])}",
            f"   Enhanced:     {fmt_curr(fnw['enhanced'])}",
            f"   Difference:   {fmt_curr(fnw['difference'])} ({fmt_pct(fnw['improvement_pct'])} improvement)",
            ""
        ])

        # Total Withdrawn
        tw = self.comparison['total_withdrawn']
        report_lines.extend([
            "💸 TOTAL WITHDRAWN:",
            f"   Original:     {fmt_curr(tw['original'])}",
            f"   Enhanced:     {fmt_curr(tw['enhanced'])}",
            f"   Difference:   {fmt_curr(tw['difference'])} ({fmt_pct(tw['improvement_pct'])} improvement)",
            ""
        ])

        # Total PnL
        pnl = self.comparison['total_pnl']
        report_lines.extend([
            "📈 TOTAL PROFIT:",
            f"   Original:     {fmt_curr(pnl['original'])}",
            f"   Enhanced:     {fmt_curr(pnl['enhanced'])}",
            f"   Difference:   {fmt_curr(pnl['difference'])} ({fmt_pct(pnl['improvement_pct'])} improvement)",
            ""
        ])

        # ROI
        roi = self.comparison['roi']
        report_lines.extend([
            "🎯 RETURN ON INVESTMENT (ROI):",
            f"   Original:     {fmt_pct(roi['original'])}",
            f"   Enhanced:     {fmt_pct(roi['enhanced'])}",
            f"   Difference:   {fmt_pct(roi['difference'])} ({fmt_pct(roi['improvement_pct'])} improvement)",
            ""
        ])

        # Trading Activity
        trades = self.comparison['total_trades']
        wr = self.comparison['win_rate']
        report_lines.extend([
            "📊 TRADING ACTIVITY:",
            f"   Total Trades (Original):   {trades['original']:,}",
            f"   Total Trades (Enhanced):   {trades['enhanced']:,}",
            f"   Difference:                {trades['difference']:+,}",
            "",
            f"   Win Rate (Original):       {fmt_pct(wr['original'])}",
            f"   Win Rate (Enhanced):       {fmt_pct(wr['enhanced'])}",
            f"   Difference:                {wr['difference']:+.2f}%",
            ""
        ])

        # Summary
        report_lines.extend([
            "=" * 100,
            "📝 SUMMARY",
            "=" * 100,
            ""
        ])

        if fnw['improvement_pct'] > 0:
            report_lines.append(f"✅ Enhanced version outperformed by {fmt_pct(fnw['improvement_pct'])}")
            report_lines.append(f"✅ Additional profit: {fmt_curr(fnw['difference'])}")
        elif fnw['improvement_pct'] < 0:
            report_lines.append(f"⚠️  Original version outperformed by {fmt_pct(abs(fnw['improvement_pct']))}")
            report_lines.append(f"⚠️  Profit difference: {fmt_curr(fnw['difference'])}")
        else:
            report_lines.append("🟰 Both versions performed equally")

        report_lines.extend([
            "",
            "🔧 ENHANCEMENT FEATURES:",
            "   ✅ Charter Compliance (PIN 841921, RR ≥ 3.2)",
            "   ✅ Smart Trailing Stops (60% activation)",
            "   ✅ Quantitative Hedging (70% frequency, 40% loss reduction)",
            "   ✅ Crisis Amplification (1.5x during downturns)",
            "   ✅ Dynamic Leverage Scaling (2x-25x)",
            "   ✅ ML Win Rate Boost (+5%)",
            "",
            "=" * 100,
            f"📁 Comparison saved: logs/golden_age_comparison.json",
            "=" * 100
        ])

        return "\n".join(report_lines)

    def save_comparison(self, output_path: str = 'logs/golden_age_comparison.json'):
        """Save comparison data to JSON file"""
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w') as f:
                json.dump(self.comparison, f, indent=2)

            logger.info(f"✅ Comparison saved to: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save comparison: {e}")
            return False


async def run_simulations():
    """Run both simulations"""
    logger.info("🚀 Starting Golden Age simulations...")

    try:
        # Check if original simulation module exists
        original_exists = Path('rbotzilla_golden_age.py').exists()
        enhanced_exists = Path('rbotzilla_golden_age_enhanced.py').exists()

        if not enhanced_exists:
            logger.error("❌ Enhanced simulation not found")
            return False

        # Run enhanced simulation
        logger.info("Running enhanced simulation...")
        import rbotzilla_golden_age_enhanced
        await rbotzilla_golden_age_enhanced.main()

        if original_exists:
            # Run original simulation
            logger.info("Running original simulation...")
            import rbotzilla_golden_age
            await rbotzilla_golden_age.main()
        else:
            logger.warning("⚠️  Original simulation not found, will compare against report if available")

        return True

    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        return False


async def main():
    """Main execution"""
    print("=" * 100)
    print("🏆 GOLDEN AGE SIMULATION COMPARISON TEST")
    print("=" * 100)
    print()

    comparator = GoldenAgeComparator()

    # Option 1: Run simulations
    print("Options:")
    print("1. Run both simulations and compare")
    print("2. Compare existing reports")
    print()

    choice = input("Select option (1 or 2): ").strip()

    if choice == '1':
        logger.info("Running simulations...")
        success = await run_simulations()
        if not success:
            logger.error("❌ Simulation run failed")
            return

    # Load reports
    logger.info("Loading reports...")

    enhanced_loaded = comparator.load_report(
        'logs/golden_age_enhanced_report.json',
        'enhanced'
    )

    original_loaded = comparator.load_report(
        'logs/golden_age_original_report.json',
        'original'
    ) or comparator.load_report(
        'logs/golden_age_report.json',
        'original'
    )

    if not enhanced_loaded:
        logger.error("❌ Enhanced report not found")
        return

    if not original_loaded:
        logger.warning("⚠️  Original report not found, comparison limited")
        return

    # Compare
    logger.info("Comparing metrics...")
    comparator.compare_metrics()

    # Generate report
    report = comparator.generate_report()
    print("\n")
    print(report)

    # Save comparison
    comparator.save_comparison()

    print("\n✅ Comparison complete!")


if __name__ == "__main__":
    asyncio.run(main())
