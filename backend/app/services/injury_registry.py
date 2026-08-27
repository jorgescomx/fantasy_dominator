"""
Comprehensive NFL Injury Intelligence Registry.
Provides verified medical diagnoses, return timelines, coaching updates, and practice participation notes.
Calculates dynamic, context-specific model discounts based on injury pathophysiology.
"""
from typing import Dict, Any, Optional

INJURY_REGISTRY: Dict[str, Dict[str, Any]] = {
    # 49ers
    "christian mccaffrey": {
        "status": "QUESTIONABLE",
        "type": "Calf Strain / Achilles Precaution",
        "timeline": "Day-to-day (Tracking for Week 1)",
        "notes": "Managing mild preseason calf tightness. Kyle Shanahan confirmed it is standard veteran workload management and CMC is projected to start Week 1.",
        "impact_summary": "12% touch-cap discount & high-speed re-injury volatility modeled",
        "discount_factor": 0.88
    },
    "ricky pearsall": {
        "status": "QUESTIONABLE",
        "type": "Hamstring / Shoulder Strain",
        "timeline": "Day-to-day (Tracking for Week 1)",
        "notes": "Working through preseason soft-tissue maintenance; participating in individual route drills.",
        "impact_summary": "12% touch-cap discount & soft-tissue re-injury volatility modeled",
        "discount_factor": 0.88
    },

    # Raiders
    "ashton jeanty": {
        "status": "QUESTIONABLE",
        "type": "Precautionary Scrimmage Tweak",
        "timeline": "Day-to-day (Expected for Season Opener)",
        "notes": "Suffered a minor lower-body tweak over the weekend scrimmage. Raiders coaching staff is holding him out of contact drills purely as a precaution.",
        "impact_summary": "5% precautionary snap variance applied; full starter ceiling intact",
        "discount_factor": 0.95
    },

    # Rams
    "puka nacua": {
        "status": "QUESTIONABLE",
        "type": "Right Knee Bursa Sac Contusion",
        "timeline": "Day-to-day (Ramping up for Week 1)",
        "notes": "Suffered a burst bursa sac during joint practices with the Chargers. Avoided ligament damage; Sean McVay confirmed he is expected ready for Week 1.",
        "impact_summary": "8% contact efficiency discount; full route participation expected",
        "discount_factor": 0.92
    },

    # Chargers
    "justin herbert": {
        "status": "QUESTIONABLE",
        "type": "Plantar Fascia (Right Foot)",
        "timeline": "Day-to-day (Out of walking boot)",
        "notes": "Diagnosed with plantar fascia injury in late July. Removed from walking boot, throwing in 7-on-7 drills, and on track for season opener.",
        "impact_summary": "10% rushing mobility discount; pocket passing volume unaffected",
        "discount_factor": 0.92
    },

    # Vikings
    "tj hockenson": {
        "status": "PUP",
        "type": "Right Knee (ACL / MCL Reconstruction)",
        "timeline": "Out Weeks 1-6 (Eligible to return Week 7)",
        "notes": "Opening the regular season on the Reserve/PUP list while completing multi-ligament knee rehabilitation.",
        "impact_summary": "100% discount (0.0 pts) — zero starting equity until officially activated",
        "discount_factor": 0.0
    },

    # Browns
    "nick chubb": {
        "status": "PUP",
        "type": "Multi-Ligament Left Knee Reconstruction",
        "timeline": "Out Weeks 1-4 (Targeting October return)",
        "notes": "Placed on Reserve/PUP list. Ramping up on-field cutting and agility work with team medical staff.",
        "impact_summary": "100% discount (0.0 pts) — zero starting equity until officially activated",
        "discount_factor": 0.0
    },
    "deshaun watson": {
        "status": "QUESTIONABLE",
        "type": "Right Shoulder (Glenoid Labrum Rehab)",
        "timeline": "Cleared / Managing maintenance days",
        "notes": "Recovered from glenoid labrum surgery. Taking full first-team reps with periodic scheduled maintenance days.",
        "impact_summary": "5% veteran maintenance variance applied; full passing volume modeled",
        "discount_factor": 0.95
    },

    # Chiefs
    "marquise brown": {
        "status": "OUT",
        "type": "Sternoclavicular Joint Dislocation",
        "timeline": "4-6 Weeks (Targeting late September)",
        "notes": "Suffered a sternoclavicular dislocation during preseason Week 1. Avoided surgery and is rehabbing on schedule.",
        "impact_summary": "100% discount (0.0 pts) — zero starting equity until officially activated",
        "discount_factor": 0.0
    },
    "hollywood brown": {
        "status": "OUT",
        "type": "Sternoclavicular Joint Dislocation",
        "timeline": "4-6 Weeks (Targeting late September)",
        "notes": "Suffered a sternoclavicular dislocation during preseason Week 1. Avoided surgery and is rehabbing on schedule.",
        "impact_summary": "100% discount (0.0 pts) — zero starting equity until officially activated",
        "discount_factor": 0.0
    },

    # Panthers
    "jonathon brooks": {
        "status": "PUP",
        "type": "ACL Reconstruction Recovery",
        "timeline": "Out Weeks 1-4 (Targeting Week 5 debut)",
        "notes": "Placed on Reserve/NFI list while finishing ACL rehab from college injury. Expected to assume lead backfield role upon return in October.",
        "impact_summary": "100% discount (0.0 pts) — zero starting equity until officially activated",
        "discount_factor": 0.0
    },

    # Colts
    "josh downs": {
        "status": "QUESTIONABLE",
        "type": "High Ankle Sprain",
        "timeline": "2-3 Weeks (Targeting Week 2-3 return)",
        "notes": "Suffered a high ankle sprain during 7-on-7 drills in camp. Progressing through rehab exercises.",
        "impact_summary": "15% lateral agility & snap restriction discount applied",
        "discount_factor": 0.85
    },

    # Saints
    "kendre miller": {
        "status": "QUESTIONABLE",
        "type": "Hamstring Strain",
        "timeline": "Week-to-week",
        "notes": "Dealing with recurring hamstring tightness throughout preseason camp.",
        "impact_summary": "15% recurring soft-tissue volatility & touch-cap discount applied",
        "discount_factor": 0.85
    },

    # Ravens
    "keaton mitchell": {
        "status": "PUP",
        "type": "ACL Reconstruction",
        "timeline": "Out Weeks 1-4 (Targeting midseason)",
        "notes": "Starting regular season on Reserve/PUP list after late 2023 ACL surgery.",
        "impact_summary": "100% discount (0.0 pts) — zero starting equity until officially activated",
        "discount_factor": 0.0
    },

    # Steelers
    "roman wilson": {
        "status": "QUESTIONABLE",
        "type": "Ankle Sprain",
        "timeline": "1-2 Weeks (Questionable for Week 1)",
        "notes": "Suffered an ankle sprain during early camp drills. Resumed straight-line running on grass.",
        "impact_summary": "10% cutting agility discount & snap ramp-up applied",
        "discount_factor": 0.90
    },

    # Falcons
    "michael penix jr": {
        "status": "QUESTIONABLE",
        "type": "Knee Surgery Rehab",
        "timeline": "Cleared for non-contact team drills",
        "notes": "Operating without physical limitations as primary backup following collegiate knee procedures.",
        "impact_summary": "5% precautionary maintenance variance applied",
        "discount_factor": 0.95
    },

    # Cardinals
    "jeremiyah love": {
        "status": "QUESTIONABLE",
        "type": "Preseason High Ankle Sprain",
        "timeline": "1-2 Weeks (Questionable for Week 1)",
        "notes": "Managing a high ankle sprain from preseason practice; undergoing daily treatment with training staff.",
        "impact_summary": "10% cutting agility discount & snap ramp-up applied",
        "discount_factor": 0.90
    }
}

# Explicit list of healthy starters mistakenly tagged in raw offseason sync
HEALTHY_STARTERS = {
    "breece hall",
    "josh jacobs",
    "devonta smith",
    "malik nabers",
    "amon ra st brown",
    "amon-ra st. brown",
    "nico collins",
    "derrick henry",
    "brian thomas jr",
    "marvin harrison jr",
    "aj brown",
    "a.j. brown",
    "jonathan taylor",
    "brock bowers",
    "kyren williams",
    "devon achane",
    "de'von achane",
    "lamar jackson",
    "josh allen",
    "jayden daniels",
    "jalen hurts",
    "trey mcbride",
    "george kittle",
    "drake london",
    "garrett wilson",
    "james cook",
    "bucky irving",
    "ladd mcconkey",
    "terry mclaurin",
    "sam laporta",
    "travis kelce",
    "tucker kraft",
    "trey benson",
    "jalen mcmillan",
    "colston loveland",
    "tyler warren",
    "evan engram",
    "jake ferguson",
    "david njoku",
    "cole kmet",
    "luther burden",
    "rome odunze",
    "brandon aubrey",
    "chris boswell",
    "patrick mahomes",
    "joe burrow",
    "cj stroud",
    "c.j. stroud",
    "kyler murray",
    "jordan love",
    "baker mayfield",
    "brock purdy",
    "caleb williams",
    "jared goff",
    "dak prescott",
    "anthony richardson",
    "bo nix",
    "tua tagovailoa",
    "drake maye",
    "trevor lawrence",
    "matthew stafford",
    "geno smith",
    "kirk cousins",
    "aaron rodgers",
    "russell wilson",
    "bryce young",
    "will levis",
    "tyler shough",
    "cam ward",
    "shedeur sanders",
    "daniel jones",
    "harrison butker",
    "justin tucker"
}

def normalize_name(name: str) -> str:
    return name.lower().replace(".", "").replace("'", "").replace("-", " ").strip()

def get_injury_details(player_name: str, raw_status: Optional[str] = None, raw_body_part: Optional[str] = None, raw_notes: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Look up curated injury intelligence or generate structured fallback."""
    norm = normalize_name(player_name)
    st = (raw_status or "").upper()

    # Explicit injury designations take precedence over static healthy-player hints.
    if st in ["ACTIVE", "HEALTHY", "CLEARED", "NONE", ""]:
        if norm not in INJURY_REGISTRY:
            return None

    if norm in HEALTHY_STARTERS and st not in ["QUESTIONABLE", "Q", "DOUBTFUL", "D", "OUT", "O", "IR", "PUP", "SUSPENDED"]:
        return None

    # 2. Check curated intelligence registry
    if norm in INJURY_REGISTRY:
        return dict(INJURY_REGISTRY[norm])

    # Also check exact key matches
    for k, v in INJURY_REGISTRY.items():
        if k == norm:
            return dict(v)

    # 3. If raw status is an active injury designation, build dynamic context
    if st in ["QUESTIONABLE", "Q", "DOUBTFUL", "D", "OUT", "O", "IR", "PUP", "SUSPENDED"]:
        body_part = (raw_body_part or "Reported Injury").strip()
        bp_lower = body_part.lower()

        if st in ["QUESTIONABLE", "Q"]:
            status_label = "QUESTIONABLE"
            timeline = "Awaiting official practice participation report"
            notes = raw_notes or f"{player_name} is listed as Questionable on the official injury report. Awaiting practice report disclosure."
            
            # Dynamic pathophysiological category discount
            if any(s in bp_lower for s in ["hamstring", "calf", "groin", "quad", "thigh", "soft tissue"]):
                impact = "12% touch-cap discount & high-speed re-injury volatility modeled"
                discount_factor = 0.88
            elif any(s in bp_lower for s in ["ankle", "foot", "toe", "plantar", "turf toe"]):
                impact = "10% cutting mobility discount & snap restriction applied"
                discount_factor = 0.90
            elif any(s in bp_lower for s in ["knee", "bursa", "contusion", "bruise", "ribs", "shoulder", "chest", "wrist"]):
                impact = "8% contact efficiency discount; full route participation expected"
                discount_factor = 0.92
            elif any(s in bp_lower for s in ["rest", "maintenance", "tweak", "precaution", "precautionary", "illness", "ill"]):
                impact = "5% precautionary snap variance applied; full starter ceiling intact"
                discount_factor = 0.95
            else:
                impact = "10% volume risk & snap management discount applied"
                discount_factor = 0.90

        elif st in ["DOUBTFUL", "D"]:
            status_label = "DOUBTFUL"
            timeline = "1-2 Weeks (Doubtful for upcoming game)"
            notes = raw_notes or f"{player_name} is doubtful for the upcoming contest."
            impact = "60% severe volume risk & emergency backup discount applied"
            discount_factor = 0.40
        elif st in ["IR", "PUP"]:
            status_label = st
            timeline = "Minimum 4 Weeks on reserve list"
            notes = raw_notes or f"{player_name} is placed on the Reserve/{st} list."
            impact = "100% discount (0.0 pts) — zero starting equity until officially activated"
            discount_factor = 0.0
        else:
            status_label = "OUT"
            timeline = "Ruled Out for upcoming game"
            notes = raw_notes or f"{player_name} has been ruled Out for the upcoming game."
            impact = "100% discount (0.0 pts) — zero starting equity until officially activated"
            discount_factor = 0.0

        return {
            "status": status_label,
            "type": f"{body_part} (Practice Report)" if raw_body_part else "Practice Report Designation",
            "timeline": timeline,
            "notes": notes,
            "impact_summary": impact,
            "discount_factor": discount_factor
        }

    return None
