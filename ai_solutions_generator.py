"""
AI-Powered Solutions Generator for Security Market Analysis
Module 4: OpenAI Integration for Problem-Solution Mapping
"""

import openai
import json
import os
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SecurityIssue:
    """Data class for security product issues"""
    company: str
    issue_type: str
    severity: str
    description: str
    evidence: str
    market_impact: str

@dataclass
class AISolution:
    """Data class for AI-generated solutions"""
    problem_id: str
    solution_title: str
    action_items: List[str]
    evidence_strategy: List[str]
    roi_projection: str
    timeline: str
    investment_required: str

class SecuritySolutionsAI:
    """AI-powered solutions generator for security market issues"""
    
    def __init__(self):
        # Load API key from environment
        self.client = None
        if os.getenv('OPENAI_API_KEY'):
            self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Predefined security issues from market analysis
        self.issues = [
            SecurityIssue(
                company="Norton",
                issue_type="Reputation Crisis",
                severity="Critical",
                description="Reddit community actively questioning 'is norton truly bad?' indicating serious brand trust issues",
                evidence="Multiple Reddit threads, performance complaints, system slowdown reports",
                market_impact="1.2M potential switchers, $889M revenue at risk"
            ),
            SecurityIssue(
                company="McAfee",
                issue_type="GDPR Violations",
                severity="Critical",
                description="Users reporting difficult account deletion and excessive data collection",
                evidence="User complaints about 'scam artists' behavior, GDPR non-compliance",
                market_impact="$50M regulatory fine risk, $549M opportunity"
            ),
            SecurityIssue(
                company="Bitdefender",
                issue_type="Market Opportunity",
                severity="Growth",
                description="Unique position in underserved Linux consumer security market",
                evidence="Linux users reporting lack of quality consumer AV, Bitdefender well-positioned",
                market_impact="$328M revenue opportunity, 200% Linux user growth potential"
            )
        ]
    
    def generate_solution(self, issue: SecurityIssue) -> AISolution:
        """Generate AI-powered solution for a security issue"""
        
        if self.client:
            prompt = f"""
            As a strategic business consultant specializing in cybersecurity markets, analyze this critical issue and provide a comprehensive solution strategy:
            
            ISSUE ANALYSIS:
            Company: {issue.company}
            Problem: {issue.issue_type} - {issue.description}
            Evidence: {issue.evidence}
            Market Impact: {issue.market_impact}
            Severity: {issue.severity}
            
            Provide a strategic solution with these components:
            1. Solution Title (concise, action-oriented)
            2. 4-5 specific action items (concrete steps)
            3. Evidence strategy (how to prove effectiveness)
            4. ROI projection (quantified business impact)
            5. Implementation timeline
            6. Investment requirements
            
            Focus on practical, measurable strategies that address root causes and create competitive advantage.
            """
            
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a senior strategy consultant with expertise in cybersecurity market dynamics and business transformation."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.7
                )
                
                content = response.choices[0].message.content
                return self._parse_ai_response(content, issue)
                
            except Exception as e:
                print(f"Error generating AI solution: {e}")
                return self._fallback_solution(issue)
        else:
            return self._fallback_solution(issue)
    
    def _parse_ai_response(self, content: str, issue: SecurityIssue) -> AISolution:
        """Parse AI response into structured solution"""
        # Simple parsing - in production, would use more sophisticated NLP
        lines = content.split('\n')
        
        solution_title = "AI-Generated Strategic Solution"
        action_items = []
        evidence_strategy = []
        
        current_section = None
        for line in lines:
            line = line.strip()
            if "solution" in line.lower() and "title" in line.lower():
                current_section = "title"
            elif "action" in line.lower():
                current_section = "actions"
            elif "evidence" in line.lower():
                current_section = "evidence"
            elif line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '•')):
                if current_section == "actions":
                    action_items.append(line)
                elif current_section == "evidence":
                    evidence_strategy.append(line)
        
        if not action_items:  # Fallback parsing
            action_items = [line for line in lines if line.startswith(('1.', '2.', '3.', '4.', '5.'))][:5]
        
        return AISolution(
            problem_id=f"{issue.company.lower()}_{issue.issue_type.lower().replace(' ', '_')}",
            solution_title=solution_title,
            action_items=action_items[:5],
            evidence_strategy=evidence_strategy[:3],
            roi_projection=f"${issue.market_impact.split('$')[-1].split()[0]} projected impact",
            timeline="6-12 months implementation",
            investment_required="$5-25M strategic investment"
        )
    
    def _fallback_solution(self, issue: SecurityIssue) -> AISolution:
        """Provide fallback solution if AI fails"""
        fallback_solutions = {
            "Norton": {
                "title": "Performance-First Recovery Strategy",
                "actions": [
                    "1. Implement lightweight scanning engine reducing CPU usage by 40%",
                    "2. Launch transparency campaign with weekly performance reports",
                    "3. Engage Reddit community with developer AMA series",
                    "4. Partner with independent testing labs for validation",
                    "5. Create performance comparison marketing vs competitors"
                ],
                "evidence": [
                    "AV-TEST certification for performance benchmarks",
                    "Independent system impact measurements",
                    "Community feedback tracking and response"
                ]
            },
            "McAfee": {
                "title": "GDPR Compliance & Privacy Leadership",
                "actions": [
                    "1. Conduct immediate third-party GDPR compliance audit",
                    "2. Implement one-click account deletion within 30 days",
                    "3. Reduce data collection to legally required minimum",
                    "4. Launch privacy-first marketing campaign",
                    "5. Establish proactive regulatory communication"
                ],
                "evidence": [
                    "External legal compliance certification",
                    "Privacy policy transparency reports",
                    "User satisfaction surveys on data practices"
                ]
            },
            "Bitdefender": {
                "title": "Linux Market Expansion Strategy",
                "actions": [
                    "1. Develop enterprise Linux security offerings",
                    "2. Partner with major Linux distributions",
                    "3. Create developer-focused marketing campaigns",
                    "4. Establish GitHub and open-source presence",
                    "5. Build command-line and automation tools"
                ],
                "evidence": [
                    "Linux community adoption metrics",
                    "Enterprise partnership agreements",
                    "Market share growth in Linux segment"
                ]
            }
        }
        
        solution_data = fallback_solutions.get(issue.company, fallback_solutions["Norton"])
        
        return AISolution(
            problem_id=f"{issue.company.lower()}_{issue.issue_type.lower().replace(' ', '_')}",
            solution_title=solution_data["title"],
            action_items=solution_data["actions"],
            evidence_strategy=solution_data["evidence"],
            roi_projection=f"${issue.market_impact.split('$')[-1].split()[0]} projected impact",
            timeline="6-12 months implementation",
            investment_required="$5-25M strategic investment"
        )
    
    def generate_all_solutions(self) -> Dict[str, AISolution]:
        """Generate solutions for all identified issues"""
        solutions = {}
        for issue in self.issues:
            solution = self.generate_solution(issue)
            solutions[solution.problem_id] = solution
        return solutions
    
    def export_solutions_json(self, solutions: Dict[str, AISolution]) -> str:
        """Export solutions to JSON format"""
        export_data = {
            "generated_at": datetime.now().isoformat(),
            "total_solutions": len(solutions),
            "solutions": {}
        }
        
        for solution_id, solution in solutions.items():
            export_data["solutions"][solution_id] = {
                "problem_id": solution.problem_id,
                "solution_title": solution.solution_title,
                "action_items": solution.action_items,
                "evidence_strategy": solution.evidence_strategy,
                "roi_projection": solution.roi_projection,
                "timeline": solution.timeline,
                "investment_required": solution.investment_required
            }
        
        return json.dumps(export_data, indent=2)

if __name__ == "__main__":
    # Example usage
    ai_solutions = SecuritySolutionsAI()
    solutions = ai_solutions.generate_all_solutions()
    
    print("🤖 AI-Powered Security Solutions Generated")
    print("=" * 50)
    
    for solution_id, solution in solutions.items():
        print(f"\n{solution.solution_title}")
        print(f"Problem ID: {solution.problem_id}")
        print(f"Timeline: {solution.timeline}")
        print(f"Investment: {solution.investment_required}")
        print(f"ROI: {solution.roi_projection}")
        print("Action Items:")
        for item in solution.action_items:
            print(f"  {item}")
        print()
    
    print("✅ AI Solutions Generator ready for Module 4 integration")