#!/usr/bin/env python3
"""
Codebase Genius - Quality Validation Framework
Phase 7: Automated documentation quality assessment

Provides comprehensive quality validation including:
- Documentation completeness analysis
- Code citation validation
- Structural quality checks
- Content accuracy verification
- Visual diagram assessment

Author: Cavin Otieno
Date: 2025-10-31
"""

import json
import re
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import markdown
from collections import Counter, defaultdict

@dataclass
class QualityScore:
    """Individual quality score component"""
    category: str
    score: float  # 0.0 to 1.0
    max_score: float = 1.0
    details: Dict[str, Any] = None
    passed: bool = False
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}
        self.passed = self.score >= (self.max_score * 0.7)  # 70% threshold

@dataclass
class QualityValidationResult:
    """Complete quality validation result"""
    document_type: str
    repository_url: str
    overall_score: float
    max_possible_score: float
    quality_scores: List[QualityScore]
    validation_timestamp: datetime
    issues_found: List[str]
    recommendations: List[str]
    generated_files: List[str]

class DocumentationQualityValidator:
    """Comprehensive documentation quality validation framework"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.results_dir = self.base_dir / "results" / "quality"
        
        # Quality assessment criteria
        self.quality_criteria = {
            "structure": {
                "weight": 0.25,
                "required_sections": [
                    "Overview", "Installation", "Usage", "API Documentation",
                    "Architecture", "Contributing", "License"
                ],
                "optional_sections": [
                    "Examples", "FAQ", "Troubleshooting", "Changelog"
                ]
            },
            "completeness": {
                "weight": 0.25,
                "min_api_functions": 5,
                "min_code_examples": 3,
                "min_architecture_diagrams": 1
            },
            "citations": {
                "weight": 0.20,
                "min_citation_coverage": 0.8,  # 80% of code elements should be cited
                "required_citation_types": ["function", "class", "module"]
            },
            "readability": {
                "weight": 0.15,
                "min_paragraph_count": 5,
                "max_sentence_length": 25,  # Average words per sentence
                "required_heading_levels": [1, 2, 3]
            },
            "technical_accuracy": {
                "weight": 0.15,
                "min_relationship_coverage": 0.7,  # 70% of relationships should be documented
                "required_diagram_types": ["architecture", "call_graph"]
            }
        }
        
        # Ensure results directory exists
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_documentation_quality(self, pipeline_results: Dict[str, Any]) -> QualityValidationResult:
        """Main quality validation entry point"""
        print("🔍 Validating documentation quality...")
        
        # Extract documentation data
        doc_data = pipeline_results.get("documentation", {})
        analysis_data = pipeline_results.get("analysis", {})
        repo_data = pipeline_results.get("repository", {})
        
        # Initialize quality scores
        quality_scores = []
        
        # Validate structure
        structure_score = self._validate_documentation_structure(doc_data)
        quality_scores.append(structure_score)
        
        # Validate completeness
        completeness_score = self._validate_completeness(doc_data, analysis_data, repo_data)
        quality_scores.append(completeness_score)
        
        # Validate citations
        citation_score = self._validate_citations(doc_data, analysis_data)
        quality_scores.append(citation_score)
        
        # Validate readability
        readability_score = self._validate_readability(doc_data)
        quality_scores.append(readability_score)
        
        # Validate technical accuracy
        accuracy_score = self._validate_technical_accuracy(doc_data, analysis_data)
        quality_scores.append(accuracy_score)
        
        # Calculate overall score
        overall_score = sum(
            score.score * self.quality_criteria[score.category]["weight"]
            for score in quality_scores
        )
        
        # Identify issues and generate recommendations
        issues = self._identify_quality_issues(quality_scores)
        recommendations = self._generate_quality_recommendations(quality_scores)
        
        # Collect generated files
        generated_files = self._collect_generated_files(doc_data)
        
        return QualityValidationResult(
            document_type="comprehensive_documentation",
            repository_url=repo_data.get("url", "unknown"),
            overall_score=overall_score,
            max_possible_score=1.0,
            quality_scores=quality_scores,
            validation_timestamp=datetime.now(),
            issues_found=issues,
            recommendations=recommendations,
            generated_files=generated_files
        )
    
    def _validate_documentation_structure(self, doc_data: Dict[str, Any]) -> QualityScore:
        """Validate documentation structure and organization"""
        print("  📋 Validating documentation structure...")
        
        details = {}
        score = 0.0
        max_score = 1.0
        
        # Extract markdown content
        markdown_content = ""
        if "markdown" in doc_data:
            markdown_content = doc_data["markdown"]
        
        # Check required sections
        required_sections = self.quality_criteria["structure"]["required_sections"]
        found_sections = []
        
        for section in required_sections:
            # Look for section headers
            patterns = [
                rf"^#\s+{section}",
                rf"^##\s+{section}",
                rf"^###\s+{section}",
                f"{section}:"  # Bullet points
            ]
            
            for pattern in patterns:
                if re.search(pattern, markdown_content, re.IGNORECASE | re.MULTILINE):
                    found_sections.append(section)
                    break
        
        details["required_sections_found"] = found_sections
        details["required_sections_total"] = len(required_sections)
        details["required_sections_coverage"] = len(found_sections) / len(required_sections)
        
        # Check optional sections
        optional_sections = self.quality_criteria["structure"]["optional_sections"]
        found_optional = []
        
        for section in optional_sections:
            if re.search(rf"^#+\s+{section}", markdown_content, re.IGNORECASE | re.MULTILINE):
                found_optional.append(section)
        
        details["optional_sections_found"] = found_optional
        
        # Check heading structure
        h1_count = len(re.findall(r"^# ", markdown_content, re.MULTILINE))
        h2_count = len(re.findall(r"^## ", markdown_content, re.MULTILINE))
        h3_count = len(re.findall(r"^### ", markdown_content, re.MULTILINE))
        
        details["heading_structure"] = {
            "h1": h1_count,
            "h2": h2_count,
            "h3": h3_count
        }
        
        # Calculate structure score
        required_coverage = details["required_sections_coverage"]
        heading_bonus = min((h1_count + h2_count + h3_count) / 10, 0.2)  # Bonus for good heading structure
        
        score = (required_coverage * 0.7) + (heading_bonus * 0.3)
        score = min(score, 1.0)  # Cap at 1.0
        
        return QualityScore(
            category="structure",
            score=score,
            max_score=max_score,
            details=details
        )
    
    def _validate_completeness(self, doc_data: Dict[str, Any], analysis_data: Dict[str, Any], repo_data: Dict[str, Any]) -> QualityScore:
        """Validate documentation completeness"""
        print("  📊 Validating documentation completeness...")
        
        details = {}
        score = 0.0
        max_score = 1.0
        
        # Extract markdown content
        markdown_content = doc_data.get("markdown", "")
        
        # Check API documentation completeness
        api_section_score = 0.0
        if "API" in markdown_content or "Functions" in markdown_content:
            # Count code blocks in API section
            code_blocks = len(re.findall(r"```[\s\S]*?```", markdown_content))
            if code_blocks >= 3:
                api_section_score = 1.0
            else:
                api_section_score = code_blocks / 3.0
        
        details["api_code_blocks"] = code_blocks if "API" in markdown_content else 0
        details["api_section_score"] = api_section_score
        
        # Check installation instructions
        install_score = 0.0
        install_keywords = ["install", "pip install", "npm install", "setup.py", "requirements.txt"]
        for keyword in install_keywords:
            if keyword.lower() in markdown_content.lower():
                install_score = 1.0
                break
        
        details["installation_score"] = install_score
        
        # Check usage examples
        usage_score = 0.0
        usage_keywords = ["example", "usage", "tutorial", "how to"]
        usage_mentions = sum(1 for keyword in usage_keywords if keyword.lower() in markdown_content.lower())
        
        if usage_mentions >= 2:
            usage_score = 1.0
        elif usage_mentions >= 1:
            usage_score = 0.5
        
        details["usage_score"] = usage_score
        
        # Check diagram presence
        diagrams_score = 0.0
        if "diagrams" in doc_data:
            diagram_count = len(doc_data["diagrams"])
            if diagram_count >= 2:  # Architecture + call graph
                diagrams_score = 1.0
            elif diagram_count >= 1:
                diagrams_score = 0.5
        
        details["diagrams_count"] = diagram_count if "diagrams" in doc_data else 0
        details["diagrams_score"] = diagrams_score
        
        # Calculate completeness score
        scores = [api_section_score, install_score, usage_score, diagrams_score]
        score = sum(scores) / len(scores)
        
        return QualityScore(
            category="completeness",
            score=score,
            max_score=max_score,
            details=details
        )
    
    def _validate_citations(self, doc_data: Dict[str, Any], analysis_data: Dict[str, Any]) -> QualityScore:
        """Validate code citations and references"""
        print("  📚 Validating code citations...")
        
        details = {}
        score = 0.0
        max_score = 1.0
        
        # Extract markdown content
        markdown_content = doc_data.get("markdown", "")
        
        # Find all code references (functions, classes, modules)
        code_refs = re.findall(r"`([^`]+)`", markdown_content)  # Inline code
        code_blocks = re.findall(r"```[\w]*\n([\s\S]*?)\n```", markdown_content)  # Code blocks
        
        total_code_references = len(code_refs) + len(code_blocks)
        
        details["code_references"] = {
            "inline": len(code_refs),
            "code_blocks": len(code_blocks),
            "total": total_code_references
        }
        
        # Check for proper citation format
        citation_patterns = [
            r"see\s+([\w\.]+)",  # "see function_name"
            r"defined\s+in\s+([\w\.]+)",  # "defined in module"
            r"from\s+([\w\.]+)",  # "from module"
        ]
        
        citations_found = 0
        for pattern in citation_patterns:
            citations_found += len(re.findall(pattern, markdown_content, re.IGNORECASE))
        
        details["citations_found"] = citations_found
        
        # Calculate citation score based on coverage
        # Assume we have CCG data with entities
        ccg_data = analysis_data.get("ccg", {})
        entities = ccg_data.get("entities", [])
        
        if entities and total_code_references:
            # Coverage ratio of cited vs total entities
            citation_coverage = min(citations_found / len(entities), 1.0)
        else:
            citation_coverage = 0.5  # Default if no entities data
        
        details["citation_coverage"] = citation_coverage
        
        # Check for proper citation format
        format_score = 1.0 if total_code_references > 0 else 0.0
        details["format_score"] = format_score
        
        score = (citation_coverage * 0.7) + (format_score * 0.3)
        
        return QualityScore(
            category="citations",
            score=score,
            max_score=max_score,
            details=details
        )
    
    def _validate_readability(self, doc_data: Dict[str, Any]) -> QualityScore:
        """Validate documentation readability"""
        print("  📖 Validating readability...")
        
        details = {}
        score = 0.0
        max_score = 1.0
        
        # Extract markdown content
        markdown_content = doc_data.get("markdown", "")
        
        # Remove markdown syntax for text analysis
        clean_text = re.sub(r'[#*_`\[\]()]', '', markdown_content)
        sentences = re.split(r'[.!?]+', clean_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Calculate average sentence length
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        details["avg_sentence_length"] = avg_sentence_length
        
        # Check sentence length score (penalize long sentences)
        if avg_sentence_length <= self.quality_criteria["readability"]["max_sentence_length"]:
            sentence_score = 1.0
        else:
            sentence_score = max(0.0, 1.0 - (avg_sentence_length - 20) / 20)  # Penalty for overly long sentences
        
        details["sentence_length_score"] = sentence_score
        
        # Check paragraph count
        paragraphs = [p.strip() for p in markdown_content.split('\n\n') if p.strip()]
        paragraph_count = len(paragraphs)
        details["paragraph_count"] = paragraph_count
        
        paragraph_score = min(paragraph_count / 10, 1.0)  # Reward more paragraphs up to 10
        details["paragraph_score"] = paragraph_score
        
        # Check for lists and formatting
        list_items = len(re.findall(r'^\s*[-*+]\s+', markdown_content, re.MULTILINE))
        details["list_items"] = list_items
        
        formatting_score = 1.0 if list_items >= 5 else (list_items / 5.0)
        details["formatting_score"] = formatting_score
        
        # Calculate overall readability score
        scores = [sentence_score, paragraph_score, formatting_score]
        score = sum(scores) / len(scores)
        
        return QualityScore(
            category="readability",
            score=score,
            max_score=max_score,
            details=details
        )
    
    def _validate_technical_accuracy(self, doc_data: Dict[str, Any], analysis_data: Dict[str, Any]) -> QualityScore:
        """Validate technical accuracy and correctness"""
        print("  🔧 Validating technical accuracy...")
        
        details = {}
        score = 0.0
        max_score = 1.0
        
        # Extract markdown content
        markdown_content = doc_data.get("markdown", "")
        
        # Check diagram presence and types
        diagrams_score = 0.0
        required_diagrams = self.quality_criteria["technical_accuracy"]["required_diagram_types"]
        diagrams = doc_data.get("diagrams", {})
        
        if diagrams:
            diagram_types_found = []
            for diagram_name, diagram_data in diagrams.items():
                if "type" in diagram_data:
                    diagram_types_found.append(diagram_data["type"])
            
            # Check for required diagram types
            required_found = sum(1 for req_type in required_diagrams if req_type in diagram_types_found)
            diagrams_score = required_found / len(required_diagrams)
        
        details["diagrams_found"] = list(diagrams.keys()) if diagrams else []
        details["required_diagrams_score"] = diagrams_score
        
        # Check relationship coverage in documentation
        relationship_score = 0.0
        ccg_data = analysis_data.get("ccg", {})
        relationships = ccg_data.get("relationships", [])
        
        if relationships:
            # Check if relationships are mentioned in documentation
            relationship_mentions = 0
            for rel in relationships:
                # Look for relationship patterns
                if "calls" in rel.get("type", "").lower():
                    if "call" in markdown_content.lower():
                        relationship_mentions += 1
                elif "imports" in rel.get("type", "").lower():
                    if "import" in markdown_content.lower():
                        relationship_mentions += 1
                elif "inherits" in rel.get("type", "").lower():
                    if "inherit" in markdown_content.lower():
                        relationship_mentions += 1
            
            relationship_coverage = relationship_mentions / len(relationships)
            relationship_score = min(relationship_coverage, 1.0)
        
        details["relationship_coverage"] = relationship_score if relationships else 0.0
        
        # Check for technical accuracy indicators
        tech_terms = ["function", "class", "method", "module", "package", "interface", "abstract"]
        tech_term_count = sum(1 for term in tech_terms if term in markdown_content.lower())
        
        tech_accuracy_score = min(tech_term_count / 5, 1.0)  # Reward proper technical terminology
        details["tech_term_count"] = tech_term_count
        details["tech_accuracy_score"] = tech_accuracy_score
        
        # Calculate overall technical accuracy score
        scores = [diagrams_score, relationship_score, tech_accuracy_score]
        score = sum(scores) / len(scores)
        
        return QualityScore(
            category="technical_accuracy",
            score=score,
            max_score=max_score,
            details=details
        )
    
    def _identify_quality_issues(self, quality_scores: List[QualityScore]) -> List[str]:
        """Identify specific quality issues"""
        issues = []
        
        for score in quality_scores:
            if not score.passed:
                category = score.category
                
                if category == "structure":
                    coverage = score.details.get("required_sections_coverage", 0)
                    if coverage < 0.5:
                        issues.append(f"Poor documentation structure: only {coverage:.1%} of required sections found")
                    elif coverage < 0.8:
                        issues.append(f"Missing some required sections: {coverage:.1%} coverage")
                
                elif category == "completeness":
                    if score.score < 0.3:
                        issues.append("Documentation lacks essential information (installation, usage, API)")
                    elif score.score < 0.6:
                        issues.append("Documentation is incomplete - missing some key sections")
                
                elif category == "citations":
                    coverage = score.details.get("citation_coverage", 0)
                    if coverage < 0.5:
                        issues.append(f"Poor code citation coverage: only {coverage:.1%} of code elements referenced")
                
                elif category == "readability":
                    avg_length = score.details.get("avg_sentence_length", 0)
                    if avg_length > 30:
                        issues.append(f"Sentences are too long on average: {avg_length:.1f} words")
                    
                    paragraphs = score.details.get("paragraph_count", 0)
                    if paragraphs < 3:
                        issues.append("Documentation has too few paragraphs - may be hard to read")
                
                elif category == "technical_accuracy":
                    diagrams_score = score.details.get("required_diagrams_score", 0)
                    if diagrams_score < 0.5:
                        issues.append("Missing required technical diagrams (architecture, call graphs)")
        
        return issues
    
    def _generate_quality_recommendations(self, quality_scores: List[QualityScore]) -> List[str]:
        """Generate quality improvement recommendations"""
        recommendations = []
        
        for score in quality_scores:
            if not score.passed or score.score < 0.8:  # Even passing scores with room for improvement
                category = score.category
                
                if category == "structure":
                    missing_sections = []
                    required_sections = self.quality_criteria["structure"]["required_sections"]
                    found_sections = score.details.get("required_sections_found", [])
                    
                    for section in required_sections:
                        if section not in found_sections:
                            missing_sections.append(section)
                    
                    if missing_sections:
                        recommendations.append(f"Add missing sections: {', '.join(missing_sections)}")
                
                elif category == "completeness":
                    api_score = score.details.get("api_section_score", 0)
                    install_score = score.details.get("installation_score", 0)
                    usage_score = score.details.get("usage_score", 0)
                    
                    if api_score < 0.5:
                        recommendations.append("Add more API documentation with code examples")
                    if install_score < 0.5:
                        recommendations.append("Add clear installation instructions")
                    if usage_score < 0.5:
                        recommendations.append("Add usage examples and tutorials")
                
                elif category == "citations":
                    coverage = score.details.get("citation_coverage", 0)
                    if coverage < 0.8:
                        recommendations.append("Increase code citation coverage by referencing more functions, classes, and modules")
                
                elif category == "readability":
                    avg_length = score.details.get("avg_sentence_length", 0)
                    if avg_length > 25:
                        recommendations.append("Break down long sentences for better readability")
                    
                    paragraphs = score.details.get("paragraph_count", 0)
                    if paragraphs < 8:
                        recommendations.append("Add more paragraphs to improve document structure")
                
                elif category == "technical_accuracy":
                    diagrams_score = score.details.get("required_diagrams_score", 0)
                    if diagrams_score < 1.0:
                        recommendations.append("Add missing technical diagrams (architecture, call graphs)")
                    
                    tech_terms = score.details.get("tech_term_count", 0)
                    if tech_terms < 5:
                        recommendations.append("Use more precise technical terminology")
        
        # General recommendations
        if all(score.passed for score in quality_scores):
            recommendations.append("Documentation quality is good - consider adding more advanced features like interactive examples")
        
        return recommendations
    
    def _collect_generated_files(self, doc_data: Dict[str, Any]) -> List[str]:
        """Collect list of generated output files"""
        files = []
        
        if "markdown" in doc_data and doc_data["markdown"]:
            files.append("documentation.md")
        
        if "diagrams" in doc_data:
            for diagram_name, diagram_data in doc_data["diagrams"].items():
                if "file_path" in diagram_data:
                    files.append(diagram_data["file_path"])
                else:
                    files.append(f"diagram_{diagram_name}.png")
        
        return files
    
    async def run_quality_validation_batch(self, pipeline_results_list: List[Dict[str, Any]]) -> List[QualityValidationResult]:
        """Run quality validation on multiple pipeline results"""
        print("🔍 Running batch quality validation...")
        
        validation_results = []
        
        for i, results in enumerate(pipeline_results_list):
            print(f"  📄 Validating document {i+1}/{len(pipeline_results_list)}")
            
            validation_result = self.validate_documentation_quality(results)
            validation_results.append(validation_result)
            
            print(f"    Score: {validation_result.overall_score:.2f}/1.00 ({validation_result.overall_score*100:.1f}%)")
        
        # Save batch results
        await self._save_batch_validation_results(validation_results)
        
        return validation_results
    
    async def _save_batch_validation_results(self, results: List[QualityValidationResult]):
        """Save batch validation results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON results
        json_file = self.results_dir / f"quality_validation_{timestamp}.json"
        json_data = {
            "timestamp": timestamp,
            "total_documents": len(results),
            "results": [asdict(result) for result in results]
        }
        
        with open(json_file, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        # Save human-readable report
        report_file = self.results_dir / f"quality_report_{timestamp}.md"
        with open(report_file, 'w') as f:
            f.write(self._generate_quality_report(results))
        
        print(f"\n💾 Quality validation results saved:")
        print(f"   📊 JSON: {json_file}")
        print(f"   📝 Report: {report_file}")
    
    def _generate_quality_report(self, results: List[QualityValidationResult]) -> str:
        """Generate human-readable quality report"""
        report = f"""# Codebase Genius Quality Validation Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Documents Validated:** {len(results)}

## Summary

"""
        
        # Calculate aggregate statistics
        total_score = sum(result.overall_score for result in results)
        avg_score = total_score / len(results) if results else 0
        
        passed_docs = len([r for r in results if r.overall_score >= 0.7])
        
        report += f"- **Average Quality Score:** {avg_score:.2f}/1.00 ({avg_score*100:.1f}%)\n"
        report += f"- **Passed Documents:** {passed_docs}/{len(results)} ({passed_docs/len(results)*100:.1f}%)\n"
        report += f"- **Failed Documents:** {len(results)-passed_docs}\n\n"
        
        # Individual results
        for i, result in enumerate(results, 1):
            status = "✅ PASS" if result.overall_score >= 0.7 else "❌ FAIL"
            
            report += f"""### Document {i}: {result.repository_url}

**Overall Score:** {result.overall_score:.2f}/1.00 ({result.overall_score*100:.1f}%) {status}

**Category Scores:**
"""
            
            for score in result.quality_scores:
                status_icon = "✅" if score.passed else "❌"
                report += f"- {score.category}: {score.score:.2f}/1.00 {status_icon}\n"
            
            if result.issues_found:
                report += "\n**Issues Found:**\n"
                for issue in result.issues_found:
                    report += f"- {issue}\n"
            
            if result.recommendations:
                report += "\n**Recommendations:**\n"
                for rec in result.recommendations:
                    report += f"- {rec}\n"
            
            report += "\n"
        
        # Overall recommendations
        report += "## Overall Recommendations\n\n"
        
        # Aggregate recommendations
        all_recommendations = []
        for result in results:
            all_recommendations.extend(result.recommendations)
        
        recommendation_counts = Counter(all_recommendations)
        for recommendation, count in recommendation_counts.most_common(5):
            report += f"- **{recommendation}** (found in {count} documents)\n"
        
        return report
    
    def print_quality_summary(self, results: List[QualityValidationResult]):
        """Print quality summary to console"""
        if not results:
            print("No quality validation results to display")
            return
        
        print("\n" + "=" * 60)
        print("📊 QUALITY VALIDATION SUMMARY")
        print("=" * 60)
        
        avg_score = sum(r.overall_score for r in results) / len(results)
        passed_count = len([r for r in results if r.overall_score >= 0.7])
        
        print(f"Documents Validated: {len(results)}")
        print(f"Average Score: {avg_score:.2f}/1.00 ({avg_score*100:.1f}%)")
        print(f"Passed: {passed_count} ✅")
        print(f"Failed: {len(results)-passed_count} ❌")
        print(f"Success Rate: {passed_count/len(results)*100:.1f}%")
        print("=" * 60)
        
        # Show worst and best performers
        sorted_results = sorted(results, key=lambda x: x.overall_score)
        
        print("\n📉 Lowest Quality:")
        for result in sorted_results[:3]:
            print(f"   {result.repository_url}: {result.overall_score:.2f}")
        
        print("\n�� Highest Quality:")
        for result in sorted_results[-3:]:
            print(f"   {result.repository_url}: {result.overall_score:.2f}")

async def main():
    """Main quality validation execution (standalone mode)"""
    import sys
    import os
    
    validator = DocumentationQualityValidator()
    
    # Check if pipeline results file is provided
    if len(sys.argv) > 1:
        results_file = sys.argv[1]
        if os.path.exists(results_file):
            with open(results_file, 'r') as f:
                pipeline_results = json.load(f)
            
            validation_result = validator.validate_documentation_quality(pipeline_results)
            
            print(f"\n📊 Quality Validation Result:")
            print(f"Overall Score: {validation_result.overall_score:.2f}/1.00")
            print(f"Status: {'✅ PASS' if validation_result.overall_score >= 0.7 else '❌ FAIL'}")
            
            if validation_result.issues_found:
                print("\n⚠️ Issues Found:")
                for issue in validation_result.issues_found:
                    print(f"  - {issue}")
            
            if validation_result.recommendations:
                print("\n💡 Recommendations:")
                for rec in validation_result.recommendations:
                    print(f"  - {rec}")
            
            return 0 if validation_result.overall_score >= 0.7 else 1
        else:
            print(f"Error: Results file {results_file} not found")
            return 1
    else:
        print("Usage: python quality_validator.py <pipeline_results.json>")
        return 1

if __name__ == "__main__":
    import asyncio
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
