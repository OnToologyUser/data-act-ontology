#!/usr/bin/env python3
"""
EU Data Act Compliance Checker - Main Executor

Run compliance checks on Data Act contracts from the command line.

Usage:
    python run_compliance_check.py contracts/my-contract.owl
    python run_compliance_check.py contracts/*.owl
    python run_compliance_check.py --directory contracts/
"""

import sys
import argparse
from pathlib import Path
from compliance_checker import (
    DataActComplianceChecker,
    ComplianceReporter
)


def main():
    """Main execution function"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='EU Data Act Compliance Checker',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check single contract
  python run_compliance_check.py contracts/b2c-contract-alice.owl
  
  # Check multiple contracts
  python run_compliance_check.py contracts/b2c-*.owl contracts/b2b-*.owl
  
  # Check all contracts in directory
  python run_compliance_check.py --directory contracts/
  
  # Export results to JSON
  python run_compliance_check.py contracts/*.owl --export report.json
  
  # Verbose mode (show detailed violations)
  python run_compliance_check.py contracts/*.owl --verbose
        """
    )
    
    parser.add_argument(
        'contracts',
        nargs='*',
        help='Path(s) to contract OWL files'
    )
    
    parser.add_argument(
        '-d', '--directory',
        help='Directory containing contract files'
    )
    
    parser.add_argument(
        '-o', '--ontology',
        default='dataact-ontology.owl',
        help='Path to base Data Act ontology (default: dataact-ontology.owl)'
    )
    
    parser.add_argument(
        '-q', '--queries',
        default='queries',
        help='Directory containing SPARQL queries (default: queries/)'
    )
    
    parser.add_argument(
        '-e', '--export',
        help='Export results to JSON file'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed violation information'
    )
    
    parser.add_argument(
        '--summary-only',
        action='store_true',
        help='Only show summary, not individual reports'
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not args.contracts and not args.directory:
        parser.print_help()
        print("\n❌ Error: Please provide contract file(s) or directory")
        return 1
    
    # Print header
    print("=" * 80)
    print("EU DATA ACT COMPLIANCE CHECKER")
    print("Regulation (EU) 2023/2854")
    print("=" * 80)
    print()
    
    try:
        # Initialize checker
        print(f"📂 Loading Data Act ontology: {args.ontology}")
        checker = DataActComplianceChecker(
            base_ontology_path=args.ontology,
            queries_dir=args.queries
        )
        print("   ✓ Ontology loaded successfully")
        print()
        
        # Collect reports
        reports = []
        
        if args.directory:
            # Check directory
            print(f"🔍 Scanning directory: {args.directory}")
            reports = checker.check_directory(args.directory)
            print(f"   ✓ Found {len(reports)} contract(s)")
        else:
            # Check individual files
            print(f"🔍 Checking {len(args.contracts)} contract(s)")
            reports = checker.check_multiple_contracts(args.contracts)
        
        if not reports:
            print("\n⚠️  No contracts to check")
            return 0
        
        # Print reports
        if not args.summary_only:
            for report in reports:
                ComplianceReporter.print_report(report, verbose=args.verbose)
        
        # Print summary
        if len(reports) > 1 or args.summary_only:
            ComplianceReporter.print_summary(reports)
        
        # Export if requested
        if args.export:
            ComplianceReporter.export_json(reports, args.export)
        
        # Return exit code
        all_compliant = all(r.overall_compliant for r in reports)
        return 0 if all_compliant else 1
        
    except FileNotFoundError as e:
        print(f"\n❌ ERROR: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())