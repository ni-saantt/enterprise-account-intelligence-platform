"""
GTM Playbook Generator Engine for Enterprise GTM Account Intelligence Platform.
Generates actionable, multi-step GTM plays for B2B outreach.
"""

from typing import Dict, Any, List

def generate_gtm_playbook(
    company: Dict[str, Any],
    priority_level: str,
    primary_contact: str,
    secondary_contact: str
) -> List[str]:
    """
    Generates a set of recommended GTM play actions based on account priority and contacts.
    
    Args:
        company: Dictionary of company parameters.
        priority_level: "High", "Medium", or "Low" priority.
        primary_contact: Primary executive role.
        secondary_contact: Secondary executive role.
        
    Returns:
        A list of strings representing the playbook sequence.
    """
    name = company.get("Company Name", "this company")
    industry = company.get("Industry", "SaaS")
    hiring = company.get("Hiring Activity", "None")
    funding = company.get("Recent Funding", "No")
    
    playbook = []
    
    if priority_level.upper() == "HIGH":
        playbook.extend([
            f"1. Executive Outreach: Direct email pitch to the {primary_contact} from the CEO's office, referencing their {funding == 'Yes' and 'recent funding' or 'industry tailwinds'}.",
            f"2. Operations Bridge: LinkedIn connection request to the {secondary_contact} with a personalized note about scaling {industry} operations.",
            f"3. ABM Retargeting: Enroll {name} in an IP-targeted LinkedIn ad campaign highlighting our {industry} platform ROI.",
            f"4. Custom Proof-of-Concept: Send a custom, pre-recorded video demo tailored for their {hiring == 'High' and 'high hiring velocity' or 'team scale'}.",
            f"5. Live Invitation: Call and pitch a VIP roundtable invitation directly addressing {industry} bottlenecks."
        ])
    elif priority_level.upper() == "MEDIUM":
        playbook.extend([
            f"1. Persona Sequence: Enroll the {primary_contact} in a multi-step email sequence tailored for {industry} software buyers.",
            f"2. Trust Building: Share a relevant B2B case study with the {secondary_contact} showing how a peer solved their scaling challenges.",
            f"3. Social Engagement: Warm up contacts by engaging with the {primary_contact}'s recent LinkedIn posts and sharing insights.",
            f"4. Product Webinar: Invite the {secondary_contact} to a live walkthrough of our enterprise product line."
        ])
    else:  # LOW
        playbook.extend([
            f"1. Automated Nurture: Place {name} into a low-frequency monthly newsletter and product update list.",
            f"2. Social Connection: Connect with the {primary_contact} on LinkedIn for long-term network growth.",
            f"3. Industry Content: Keep contacts warm with automated reports on macro-trends in {industry}."
        ])
        
    return playbook
