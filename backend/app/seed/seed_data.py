"""Seed script for Continental Park Stadium demo data.

Populates the database with realistic zones, gates, facilities,
transport options, and FAQ entries for a fictional FIFA 2026 venue.

Usage:
    python -m app.seed.seed_data

Idempotent: safe to run multiple times. Uses merge() to upsert
records by primary key — existing records are updated, new ones
are inserted.

Note on Hindi translations:
    Translations are AI-generated and not professionally reviewed.
    See README "Known Limitations" section.
"""

from __future__ import annotations

import asyncio
import sys

import structlog

from app.core.config import get_settings
from app.core.database import Base, close_engine, create_tables, init_engine
from app.models.crowd_snapshot import CrowdSnapshot  # noqa: F401 — register model
from app.models.facility import Facility
from app.models.faq import FAQEntry
from app.models.gate import Gate
from app.models.transport import TransportOption
from app.models.zone import Zone

logger = structlog.get_logger(__name__)


# ─────────────────────────────────────────────────────────────
# Zone Data
# ─────────────────────────────────────────────────────────────
ZONES: list[dict] = [
    {
        "id": "north_stand",
        "name": "North Stand",
        "name_hi": "उत्तरी स्टैंड",
        "capacity": 15000,
        "zone_type": "seating",
        "description": "Main seating area behind the north goal. Sections N1-N12.",
        "description_hi": "उत्तरी गोल के पीछे मुख्य बैठक क्षेत्र। सेक्शन N1-N12।",
    },
    {
        "id": "south_stand",
        "name": "South Stand",
        "name_hi": "दक्षिणी स्टैंड",
        "capacity": 15000,
        "zone_type": "seating",
        "description": "Main seating area behind the south goal. Sections S1-S12.",
        "description_hi": "दक्षिणी गोल के पीछे मुख्य बैठक क्षेत्र। सेक्शन S1-S12।",
    },
    {
        "id": "east_stand",
        "name": "East Stand",
        "name_hi": "पूर्वी स्टैंड",
        "capacity": 12000,
        "zone_type": "seating",
        "description": "Side seating along the east touchline. Sections E1-E10. Includes family section.",
        "description_hi": "पूर्वी टचलाइन के साथ बैठक क्षेत्र। सेक्शन E1-E10। परिवार सेक्शन शामिल।",
    },
    {
        "id": "west_stand",
        "name": "West Stand",
        "name_hi": "पश्चिमी स्टैंड",
        "capacity": 12000,
        "zone_type": "seating",
        "description": "Side seating along the west touchline. Sections W1-W10. Press box located here.",
        "description_hi": "पश्चिमी टचलाइन के साथ बैठक क्षेत्र। सेक्शन W1-W10। प्रेस बॉक्स यहाँ स्थित।",
    },
    {
        "id": "vip_west",
        "name": "VIP Lounge West",
        "name_hi": "वीआईपी लाउंज पश्चिम",
        "capacity": 3000,
        "zone_type": "vip",
        "description": "Premium hospitality area with climate-controlled lounges, fine dining, and pitch-side views.",
        "description_hi": "वातानुकूलित लाउंज, फाइन डाइनिंग और पिच-साइड व्यू के साथ प्रीमियम आतिथ्य क्षेत्र।",
    },
    {
        "id": "concourse_n",
        "name": "North Concourse",
        "name_hi": "उत्तरी कॉन्कोर्स",
        "capacity": 5000,
        "zone_type": "concourse",
        "description": "Open walkway connecting North Stand gates. Food vendors and restrooms throughout.",
        "description_hi": "उत्तरी स्टैंड गेट्स को जोड़ने वाला खुला वॉकवे। खाद्य विक्रेता और शौचालय उपलब्ध।",
    },
    {
        "id": "concourse_s",
        "name": "South Concourse",
        "name_hi": "दक्षिणी कॉन्कोर्स",
        "capacity": 5000,
        "zone_type": "concourse",
        "description": "Open walkway connecting South Stand gates. Merchandise shops and information desks.",
        "description_hi": "दक्षिणी स्टैंड गेट्स को जोड़ने वाला खुला वॉकवे। मर्चेंडाइज़ दुकानें और सूचना डेस्क।",
    },
    {
        "id": "fan_zone",
        "name": "Fan Zone",
        "name_hi": "फैन ज़ोन",
        "capacity": 8000,
        "zone_type": "concourse",
        "description": "Outdoor entertainment area with giant screens, food trucks, and interactive activities. Open 3 hours before kickoff.",
        "description_hi": "विशाल स्क्रीन, फूड ट्रक और इंटरैक्टिव गतिविधियों वाला आउटडोर मनोरंजन क्षेत्र। किकऑफ से 3 घंटे पहले खुलता है।",
    },
]


# ─────────────────────────────────────────────────────────────
# Gate Data
# ─────────────────────────────────────────────────────────────
GATES: list[dict] = [
    {
        "id": "gate_1",
        "name": "Gate 1",
        "name_hi": "गेट 1",
        "zone_id": "north_stand",
        "gate_type": "entry",
        "is_accessible": False,
        "capacity_per_minute": 120,
    },
    {
        "id": "gate_2",
        "name": "Gate 2",
        "name_hi": "गेट 2",
        "zone_id": "north_stand",
        "gate_type": "entry",
        "is_accessible": False,
        "capacity_per_minute": 100,
    },
    {
        "id": "gate_3",
        "name": "Gate 3",
        "name_hi": "गेट 3",
        "zone_id": "east_stand",
        "gate_type": "both",
        "is_accessible": False,
        "capacity_per_minute": 150,
    },
    {
        "id": "gate_4",
        "name": "Gate 4",
        "name_hi": "गेट 4",
        "zone_id": "east_stand",
        "gate_type": "entry",
        "is_accessible": False,
        "capacity_per_minute": 100,
    },
    {
        "id": "gate_5",
        "name": "Gate 5",
        "name_hi": "गेट 5",
        "zone_id": "south_stand",
        "gate_type": "entry",
        "is_accessible": False,
        "capacity_per_minute": 120,
    },
    {
        "id": "gate_6",
        "name": "Gate 6",
        "name_hi": "गेट 6",
        "zone_id": "south_stand",
        "gate_type": "both",
        "is_accessible": False,
        "capacity_per_minute": 150,
    },
    {
        "id": "gate_7",
        "name": "Gate 7",
        "name_hi": "गेट 7",
        "zone_id": "west_stand",
        "gate_type": "entry",
        "is_accessible": False,
        "capacity_per_minute": 100,
    },
    {
        "id": "gate_8",
        "name": "Gate 8",
        "name_hi": "गेट 8",
        "zone_id": "west_stand",
        "gate_type": "entry",
        "is_accessible": False,
        "capacity_per_minute": 100,
    },
    {
        "id": "gate_a1",
        "name": "Accessible Gate A1",
        "name_hi": "सुगम्य गेट A1",
        "zone_id": "north_stand",
        "gate_type": "entry",
        "is_accessible": True,
        "capacity_per_minute": 60,
    },
    {
        "id": "gate_a2",
        "name": "Accessible Gate A2",
        "name_hi": "सुगम्य गेट A2",
        "zone_id": "south_stand",
        "gate_type": "entry",
        "is_accessible": True,
        "capacity_per_minute": 60,
    },
    {
        "id": "gate_vip",
        "name": "VIP Entrance",
        "name_hi": "वीआईपी प्रवेश",
        "zone_id": "vip_west",
        "gate_type": "entry",
        "is_accessible": True,
        "capacity_per_minute": 50,
    },
    {
        "id": "gate_e1",
        "name": "Emergency Exit East",
        "name_hi": "पूर्वी आपातकालीन निकास",
        "zone_id": "east_stand",
        "gate_type": "exit",
        "is_accessible": True,
        "capacity_per_minute": 200,
    },
]


# ─────────────────────────────────────────────────────────────
# Facility Data
# ─────────────────────────────────────────────────────────────
FACILITIES: list[dict] = [
    # ── Restrooms ────────────────────────────────────────────
    {
        "name": "Restroom Block N1",
        "name_hi": "शौचालय ब्लॉक N1",
        "zone_id": "concourse_n",
        "facility_type": "restroom",
        "is_accessible": True,
        "floor_level": 0,
        "description": "Large restroom block near Gate 1. Includes accessible stalls with grab bars.",
        "description_hi": "गेट 1 के पास बड़ा शौचालय ब्लॉक। ग्रैब बार के साथ सुगम्य स्टॉल शामिल।",
    },
    {
        "name": "Restroom Block S1",
        "name_hi": "शौचालय ब्लॉक S1",
        "zone_id": "concourse_s",
        "facility_type": "restroom",
        "is_accessible": True,
        "floor_level": 0,
        "description": "Large restroom block near Gate 5. Includes accessible stalls and baby changing station.",
        "description_hi": "गेट 5 के पास बड़ा शौचालय ब्लॉक। सुगम्य स्टॉल और बेबी चेंजिंग स्टेशन शामिल।",
    },
    {
        "name": "Restroom East Upper",
        "name_hi": "शौचालय पूर्वी ऊपरी",
        "zone_id": "east_stand",
        "facility_type": "restroom",
        "is_accessible": False,
        "floor_level": 1,
        "description": "Upper level restrooms near sections E5-E8.",
        "description_hi": "सेक्शन E5-E8 के पास ऊपरी स्तर के शौचालय।",
    },
    {
        "name": "VIP Restroom",
        "name_hi": "वीआईपी शौचालय",
        "zone_id": "vip_west",
        "facility_type": "restroom",
        "is_accessible": True,
        "floor_level": 1,
        "description": "Premium restroom facilities in VIP lounge.",
        "description_hi": "वीआईपी लाउंज में प्रीमियम शौचालय सुविधाएं।",
    },
    # ── First Aid ────────────────────────────────────────────
    {
        "name": "First Aid Station North",
        "name_hi": "प्राथमिक चिकित्सा केंद्र उत्तर",
        "zone_id": "concourse_n",
        "facility_type": "first_aid",
        "is_accessible": True,
        "floor_level": 0,
        "description": "Staffed medical station with AED, wheelchair access, and basic treatment. Open throughout event.",
        "description_hi": "AED, व्हीलचेयर एक्सेस और बुनियादी उपचार के साथ स्टाफ मेडिकल स्टेशन। पूरे आयोजन के दौरान खुला।",
    },
    {
        "name": "First Aid Station South",
        "name_hi": "प्राथमिक चिकित्सा केंद्र दक्षिण",
        "zone_id": "concourse_s",
        "facility_type": "first_aid",
        "is_accessible": True,
        "floor_level": 0,
        "description": "Staffed medical station with AED and cooling area. Near Gate 6.",
        "description_hi": "AED और कूलिंग एरिया के साथ स्टाफ मेडिकल स्टेशन। गेट 6 के पास।",
    },
    # ── Food & Beverage ──────────────────────────────────────
    {
        "name": "Street Food Court",
        "name_hi": "स्ट्रीट फूड कोर्ट",
        "zone_id": "fan_zone",
        "facility_type": "food_beverage",
        "is_accessible": True,
        "floor_level": 0,
        "description": "International food trucks with halal, vegetarian, and vegan options. Cash and card accepted.",
        "description_hi": "हलाल, शाकाहारी और वीगन विकल्पों के साथ अंतरराष्ट्रीय फूड ट्रक। नकद और कार्ड स्वीकार्य।",
    },
    {
        "name": "North Concession Stand",
        "name_hi": "उत्तरी कन्सेशन स्टैंड",
        "zone_id": "concourse_n",
        "facility_type": "food_beverage",
        "is_accessible": True,
        "floor_level": 0,
        "description": "Quick-service beverages, snacks, and light meals. Located near sections N4-N6.",
        "description_hi": "क्विक-सर्विस पेय, स्नैक्स और हल्का भोजन। सेक्शन N4-N6 के पास स्थित।",
    },
    {
        "name": "South Concession Stand",
        "name_hi": "दक्षिणी कन्सेशन स्टैंड",
        "zone_id": "concourse_s",
        "facility_type": "food_beverage",
        "is_accessible": True,
        "floor_level": 0,
        "description": "Quick-service beverages, snacks, and light meals. Located near sections S4-S6.",
        "description_hi": "क्विक-सर्विस पेय, स्नैक्स और हल्का भोजन। सेक्शन S4-S6 के पास स्थित।",
    },
    {
        "name": "VIP Dining",
        "name_hi": "वीआईपी डाइनिंग",
        "zone_id": "vip_west",
        "facility_type": "food_beverage",
        "is_accessible": True,
        "floor_level": 1,
        "description": "Full-service restaurant and bar with pitch views. Pre-booking recommended.",
        "description_hi": "पिच व्यू के साथ फुल-सर्विस रेस्तरां और बार। पूर्व बुकिंग अनुशंसित।",
    },
    # ── Prayer Room ──────────────────────────────────────────
    {
        "name": "Multi-Faith Prayer Room",
        "name_hi": "बहु-धर्म प्रार्थना कक्ष",
        "zone_id": "concourse_n",
        "facility_type": "prayer_room",
        "is_accessible": True,
        "floor_level": 0,
        "description": "Quiet prayer and meditation space. Ablution facilities available. Open to all faiths.",
        "description_hi": "शांत प्रार्थना और ध्यान स्थान। वज़ू की सुविधा उपलब्ध। सभी धर्मों के लिए खुला।",
    },
    # ── Baby Care ────────────────────────────────────────────
    {
        "name": "Family Care Room",
        "name_hi": "फैमिली केयर रूम",
        "zone_id": "concourse_s",
        "facility_type": "baby_care",
        "is_accessible": True,
        "floor_level": 0,
        "description": "Private nursing room with changing tables, microwave, and comfortable seating.",
        "description_hi": "चेंजिंग टेबल, माइक्रोवेव और आरामदायक बैठक के साथ निजी नर्सिंग रूम।",
    },
    # ── Lost & Found ─────────────────────────────────────────
    {
        "name": "Lost & Found Desk",
        "name_hi": "खोया-पाया डेस्क",
        "zone_id": "concourse_s",
        "facility_type": "lost_found",
        "is_accessible": True,
        "floor_level": 0,
        "description": "Report or collect lost items. Open until 2 hours after final whistle. Near Gate 6.",
        "description_hi": "खोई हुई वस्तुओं की रिपोर्ट करें या लें। अंतिम सीटी के 2 घंटे बाद तक खुला। गेट 6 के पास।",
    },
]


# ─────────────────────────────────────────────────────────────
# Transport Data
# ─────────────────────────────────────────────────────────────
TRANSPORT_OPTIONS: list[dict] = [
    {
        "name": "Metro Line 3 — Stadium Station",
        "name_hi": "मेट्रो लाइन 3 — स्टेडियम स्टेशन",
        "transport_type": "metro",
        "nearest_gate_id": "gate_3",
        "estimated_walk_minutes": 5,
        "accessibility_notes": "Fully accessible: elevators, tactile paths, and platform screen doors.",
        "accessibility_notes_hi": "पूर्ण सुगम्य: लिफ्ट, स्पर्शनीय पथ और प्लेटफॉर्म स्क्रीन दरवाज़े।",
        "schedule_info": "Every 4 minutes on match days. Extended service until 1 AM post-match.",
        "schedule_info_hi": "मैच के दिनों में हर 4 मिनट। मैच के बाद रात 1 बजे तक विस्तारित सेवा।",
    },
    {
        "name": "Bus Route 42 — Continental Park Stop",
        "name_hi": "बस रूट 42 — कॉन्टिनेंटल पार्क स्टॉप",
        "transport_type": "bus",
        "nearest_gate_id": "gate_5",
        "estimated_walk_minutes": 8,
        "accessibility_notes": "Low-floor buses with wheelchair ramps. Audio announcements in English and Hindi.",
        "accessibility_notes_hi": "व्हीलचेयर रैंप के साथ लो-फ्लोर बसें। अंग्रेज़ी और हिंदी में ऑडियो घोषणाएं।",
        "schedule_info": "Every 10 minutes. Extra services 2 hours before and after match.",
        "schedule_info_hi": "हर 10 मिनट। मैच से 2 घंटे पहले और बाद में अतिरिक्त सेवाएं।",
    },
    {
        "name": "Official Taxi Stand — East Parking",
        "name_hi": "अधिकृत टैक्सी स्टैंड — पूर्वी पार्किंग",
        "transport_type": "taxi",
        "nearest_gate_id": "gate_4",
        "estimated_walk_minutes": 6,
        "accessibility_notes": "Wheelchair-accessible vehicles available on request.",
        "accessibility_notes_hi": "अनुरोध पर व्हीलचेयर-सुगम्य वाहन उपलब्ध।",
        "schedule_info": "Available throughout match day. Expect 15-20 min waits post-match.",
        "schedule_info_hi": "पूरे मैच डे उपलब्ध। मैच के बाद 15-20 मिनट की प्रतीक्षा अपेक्षित।",
    },
    {
        "name": "Rideshare Pickup — North Drop Zone",
        "name_hi": "राइडशेयर पिकअप — उत्तरी ड्रॉप ज़ोन",
        "transport_type": "rideshare",
        "nearest_gate_id": "gate_1",
        "estimated_walk_minutes": 4,
        "accessibility_notes": "Designated accessible pickup area with covered waiting.",
        "accessibility_notes_hi": "कवर्ड वेटिंग के साथ नामित सुगम्य पिकअप क्षेत्र।",
        "schedule_info": "Open throughout event. Surge pricing likely post-match.",
        "schedule_info_hi": "पूरे आयोजन के दौरान खुला। मैच के बाद सर्ज प्राइसिंग संभव।",
    },
    {
        "name": "Parking Lot A — West Entrance",
        "name_hi": "पार्किंग लॉट A — पश्चिमी प्रवेश",
        "transport_type": "parking",
        "nearest_gate_id": "gate_7",
        "estimated_walk_minutes": 10,
        "accessibility_notes": "50 reserved accessible spaces near elevator. Blue badge required.",
        "accessibility_notes_hi": "लिफ्ट के पास 50 आरक्षित सुगम्य स्थान। ब्लू बैज आवश्यक।",
        "schedule_info": "Opens 4 hours before kickoff. Expect 30-45 min exit delay post-match.",
        "schedule_info_hi": "किकऑफ से 4 घंटे पहले खुलता है। मैच के बाद 30-45 मिनट निकासी विलंब अपेक्षित।",
    },
]


# ─────────────────────────────────────────────────────────────
# FAQ Data
# ─────────────────────────────────────────────────────────────
FAQ_ENTRIES: list[dict] = [
    # ── General ──────────────────────────────────────────────
    {
        "question": "What are the stadium opening hours on match day?",
        "question_hi": "मैच के दिन स्टेडियम खुलने का समय क्या है?",
        "answer": "Gates open 3 hours before kickoff. The Fan Zone opens simultaneously. We recommend arriving at least 90 minutes early to clear security and find your seat comfortably.",
        "answer_hi": "गेट किकऑफ से 3 घंटे पहले खुलते हैं। फैन ज़ोन भी उसी समय खुलता है। हम सुरक्षा जांच और अपनी सीट आराम से खोजने के लिए कम से कम 90 मिनट पहले पहुंचने की सलाह देते हैं।",
        "category": "general",
        "tags": "hours,opening,timing,gates,when",
    },
    {
        "question": "What items are prohibited inside the stadium?",
        "question_hi": "स्टेडियम के अंदर कौन सी वस्तुएं प्रतिबंधित हैं?",
        "answer": "Prohibited items include: bags larger than 30x30x15cm, glass containers, alcohol, fireworks, laser pointers, professional cameras (lens > 200mm), flags on poles, and any weapons. Small clear bags are recommended for faster entry.",
        "answer_hi": "प्रतिबंधित वस्तुओं में शामिल हैं: 30x30x15cm से बड़े बैग, कांच के कंटेनर, शराब, पटाखे, लेज़र पॉइंटर, प्रोफेशनल कैमरे (लेंस > 200mm), पोल पर झंडे, और कोई भी हथियार। तेज़ प्रवेश के लिए छोटे पारदर्शी बैग की सिफारिश की जाती है।",
        "category": "rules",
        "tags": "prohibited,banned,items,bags,security,rules",
    },
    {
        "question": "Is there free WiFi inside the stadium?",
        "question_hi": "क्या स्टेडियम के अंदर मुफ्त वाईफाई है?",
        "answer": "Yes, free WiFi is available throughout the stadium. Connect to 'ContinentalPark_Free' and accept the terms. Coverage is best in concourse areas. For streaming-quality connection, premium WiFi is available for purchase.",
        "answer_hi": "हाँ, पूरे स्टेडियम में मुफ्त वाईफाई उपलब्ध है। 'ContinentalPark_Free' से कनेक्ट करें और शर्तें स्वीकार करें। कॉन्कोर्स क्षेत्रों में कवरेज सबसे अच्छा है। स्ट्रीमिंग-क्वालिटी कनेक्शन के लिए प्रीमियम वाईफाई खरीदा जा सकता है।",
        "category": "general",
        "tags": "wifi,internet,connectivity,free",
    },
    # ── Accessibility ────────────────────────────────────────
    {
        "question": "What accessibility features are available at the stadium?",
        "question_hi": "स्टेडियम में कौन सी सुगम्यता सुविधाएं उपलब्ध हैं?",
        "answer": "Continental Park Stadium offers: wheelchair-accessible seating in all stands, two dedicated accessible gates (A1, A2) with ramps, accessible restrooms on every level, hearing loop systems, sign language interpreters on request, tactile wayfinding paths, and service animal relief areas. Contact our accessibility desk at the South Concourse for assistance.",
        "answer_hi": "कॉन्टिनेंटल पार्क स्टेडियम प्रदान करता है: सभी स्टैंडों में व्हीलचेयर-सुगम्य बैठक, रैंप के साथ दो समर्पित सुगम्य गेट (A1, A2), हर स्तर पर सुगम्य शौचालय, हियरिंग लूप सिस्टम, अनुरोध पर सांकेतिक भाषा दुभाषिए, स्पर्शनीय वेफाइंडिंग पथ, और सेवा पशु राहत क्षेत्र। सहायता के लिए दक्षिणी कॉन्कोर्स पर हमारे सुगम्यता डेस्क से संपर्क करें।",
        "category": "accessibility",
        "tags": "wheelchair,accessible,disability,ramp,hearing,sign language",
    },
    {
        "question": "Where are the wheelchair-accessible entrances?",
        "question_hi": "व्हीलचेयर-सुगम्य प्रवेश द्वार कहाँ हैं?",
        "answer": "Wheelchair-accessible entrances are at Gate A1 (North Stand) and Gate A2 (South Stand). Both have level access with no steps, wide turnstiles, and dedicated staff. The VIP Entrance is also fully accessible. Rideshare drop-off at the North Drop Zone is closest to Gate A1 (4 min walk on flat surface).",
        "answer_hi": "व्हीलचेयर-सुगम्य प्रवेश द्वार गेट A1 (उत्तरी स्टैंड) और गेट A2 (दक्षिणी स्टैंड) पर हैं। दोनों में बिना सीढ़ियों के समतल पहुंच, चौड़े टर्नस्टाइल और समर्पित स्टाफ हैं। वीआईपी प्रवेश भी पूर्ण सुगम्य है। उत्तरी ड्रॉप ज़ोन पर राइडशेयर ड्रॉप-ऑफ गेट A1 के सबसे करीब है (समतल सतह पर 4 मिनट की पैदल दूरी)।",
        "category": "accessibility",
        "tags": "wheelchair,entrance,gate,accessible,ramp",
    },
    # ── Safety ───────────────────────────────────────────────
    {
        "question": "Where can I find first aid or medical assistance?",
        "question_hi": "मुझे प्राथमिक चिकित्सा या चिकित्सा सहायता कहाँ मिल सकती है?",
        "answer": "First aid stations are located at the North Concourse (near Gate 1) and South Concourse (near Gate 6). Both are staffed with trained medical personnel, equipped with AEDs, and accessible. For emergencies, alert any steward or call the stadium emergency line displayed on screens.",
        "answer_hi": "प्राथमिक चिकित्सा केंद्र उत्तरी कॉन्कोर्स (गेट 1 के पास) और दक्षिणी कॉन्कोर्स (गेट 6 के पास) पर स्थित हैं। दोनों में प्रशिक्षित चिकित्सा कर्मी, AED उपकरण और सुगम्यता है। आपातकाल के लिए, किसी भी स्टीवर्ड को सचेत करें या स्क्रीन पर प्रदर्शित स्टेडियम आपातकालीन लाइन पर कॉल करें।",
        "category": "safety",
        "tags": "first aid,medical,emergency,doctor,health,AED",
    },
    {
        "question": "What should I do in case of an emergency evacuation?",
        "question_hi": "आपातकालीन निकासी की स्थिति में मुझे क्या करना चाहिए?",
        "answer": "Follow the green emergency exit signs and steward instructions. Each zone has marked evacuation routes leading to assembly points outside the stadium. Emergency Exit East (Gate E1) has the highest capacity. Do not use elevators during evacuation. Assistance for mobility-impaired fans is available at every stairwell.",
        "answer_hi": "हरे आपातकालीन निकास चिह्नों और स्टीवर्ड निर्देशों का पालन करें। प्रत्येक ज़ोन में स्टेडियम के बाहर एसेंबली पॉइंट तक जाने वाले चिह्नित निकासी मार्ग हैं। आपातकालीन निकास पूर्व (गेट E1) की क्षमता सबसे अधिक है। निकासी के दौरान लिफ्ट का उपयोग न करें। गतिशीलता-बाधित प्रशंसकों के लिए हर सीढ़ी पर सहायता उपलब्ध है।",
        "category": "safety",
        "tags": "emergency,evacuation,exit,safety,fire",
    },
    # ── Food ─────────────────────────────────────────────────
    {
        "question": "What food options are available, including dietary restrictions?",
        "question_hi": "आहार प्रतिबंधों सहित कौन से खाद्य विकल्प उपलब्ध हैं?",
        "answer": "The stadium offers diverse food options: halal-certified food trucks in the Fan Zone, vegetarian and vegan stands at North and South Concessions, gluten-free options marked with green labels, and kosher meals available on pre-order. All allergens are clearly labeled. The VIP Dining restaurant accommodates all dietary requirements with advance notice.",
        "answer_hi": "स्टेडियम विविध खाद्य विकल्प प्रदान करता है: फैन ज़ोन में हलाल-प्रमाणित फूड ट्रक, उत्तरी और दक्षिणी कन्सेशन पर शाकाहारी और वीगन स्टैंड, हरे लेबल से चिह्नित ग्लूटेन-फ्री विकल्प, और पूर्व-आदेश पर कोशर भोजन उपलब्ध। सभी एलर्जेन स्पष्ट रूप से लेबल किए गए हैं। वीआईपी डाइनिंग रेस्तरां पूर्व सूचना के साथ सभी आहार आवश्यकताओं को पूरा करता है।",
        "category": "food",
        "tags": "food,eat,halal,vegetarian,vegan,gluten,kosher,restaurant",
    },
    {
        "question": "Can I bring my own food and drinks?",
        "question_hi": "क्या मैं अपना खाना और पेय ला सकता हूँ?",
        "answer": "Small snacks and one sealed water bottle (up to 500ml) per person are allowed. No glass containers, alcohol, or large coolers. Baby food and medically required items are always permitted — inform security at entry.",
        "answer_hi": "छोटे स्नैक्स और प्रति व्यक्ति एक सील बंद पानी की बोतल (500ml तक) की अनुमति है। कोई कांच के कंटेनर, शराब, या बड़े कूलर नहीं। बेबी फूड और चिकित्सकीय रूप से आवश्यक वस्तुओं की हमेशा अनुमति है — प्रवेश पर सुरक्षा को सूचित करें।",
        "category": "food",
        "tags": "food,drink,bring,water,bottle,outside",
    },
    # ── Transport ────────────────────────────────────────────
    {
        "question": "How do I get to the stadium by public transport?",
        "question_hi": "मैं सार्वजनिक परिवहन से स्टेडियम कैसे पहुँचूँ?",
        "answer": "Metro Line 3 to 'Stadium Station' is the fastest option (5 min walk to Gate 3, trains every 4 min on match days). Bus Route 42 stops at 'Continental Park Stop' (8 min walk to Gate 5, buses every 10 min). Both services run extended hours on match days until 1 AM.",
        "answer_hi": "'स्टेडियम स्टेशन' तक मेट्रो लाइन 3 सबसे तेज़ विकल्प है (गेट 3 तक 5 मिनट की पैदल दूरी, मैच के दिनों में हर 4 मिनट में ट्रेन)। बस रूट 42 'कॉन्टिनेंटल पार्क स्टॉप' पर रुकती है (गेट 5 तक 8 मिनट की पैदल दूरी, हर 10 मिनट में बस)। दोनों सेवाएं मैच के दिनों में रात 1 बजे तक विस्तारित घंटों में चलती हैं।",
        "category": "transport",
        "tags": "metro,bus,public,transport,train,how to get",
    },
    {
        "question": "Where can I park my car?",
        "question_hi": "मैं अपनी कार कहाँ पार्क कर सकता हूँ?",
        "answer": "Parking Lot A is accessible from the west entrance (10 min walk to Gate 7). It opens 4 hours before kickoff. 50 accessible parking spaces are available near the elevator (blue badge required). Expect 30-45 minute exit delays after the match. We strongly recommend public transport for faster departure.",
        "answer_hi": "पार्किंग लॉट A पश्चिमी प्रवेश से सुलभ है (गेट 7 तक 10 मिनट की पैदल दूरी)। यह किकऑफ से 4 घंटे पहले खुलता है। लिफ्ट के पास 50 सुगम्य पार्किंग स्थान उपलब्ध हैं (ब्लू बैज आवश्यक)। मैच के बाद 30-45 मिनट की निकासी देरी की उम्मीद करें। हम तेज़ प्रस्थान के लिए सार्वजनिक परिवहन की दृढ़ता से सिफारिश करते हैं।",
        "category": "transport",
        "tags": "parking,car,drive,lot,space",
    },
]


# ─────────────────────────────────────────────────────────────
# Seeder Logic
# ─────────────────────────────────────────────────────────────
async def seed_database() -> None:
    """Populate the database with Continental Park Stadium demo data.

    Uses merge() for upsert semantics — safe to run multiple times.
    Records with existing primary keys are updated; new ones are inserted.
    """
    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
    from sqlalchemy import select
    from app.models.zone import Zone

    from app.core.database import _async_session_factory

    if _async_session_factory is None:
        raise RuntimeError("Database not initialized. Call init_engine() first.")

    session_factory: async_sessionmaker[AsyncSession] = _async_session_factory

    async with session_factory() as session:
        # Check if already seeded to prevent duplicate auto-increment records
        result = await session.execute(select(Zone).limit(1))
        if result.scalars().first() is not None:
            logger.info("database_already_seeded")
            return

        # Zones
        for zone_data in ZONES:
            zone = Zone(**zone_data)
            await session.merge(zone)
        logger.info("seeded_zones", count=len(ZONES))

        # Gates
        for gate_data in GATES:
            gate = Gate(**gate_data)
            await session.merge(gate)
        logger.info("seeded_gates", count=len(GATES))

        # Facilities (auto-increment PK, so we check by name+zone)
        for fac_data in FACILITIES:
            facility = Facility(**fac_data)
            session.add(facility)
        logger.info("seeded_facilities", count=len(FACILITIES))

        # Transport options
        for transport_data in TRANSPORT_OPTIONS:
            option = TransportOption(**transport_data)
            session.add(option)
        logger.info("seeded_transport_options", count=len(TRANSPORT_OPTIONS))

        # FAQ entries
        for faq_data in FAQ_ENTRIES:
            entry = FAQEntry(**faq_data)
            session.add(entry)
        logger.info("seeded_faq_entries", count=len(FAQ_ENTRIES))

        await session.commit()
        logger.info("seed_complete", stadium="Continental Park Stadium")


async def _main() -> None:
    """Entry point for running seed as a standalone script."""
    from app.core.logging import setup_logging

    settings = get_settings()
    setup_logging(debug=settings.debug)

    logger.info("starting_seed", database=settings.database_url)
    init_engine(settings.database_url, echo=False)
    await create_tables()
    await seed_database()
    await close_engine()
    logger.info("seed_finished")


if __name__ == "__main__":
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        sys.exit(0)
