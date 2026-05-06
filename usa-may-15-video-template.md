# Evergreen-Where-To-Move-For-AI-Jobs-USA-May15
## Where Should You Move to Work in AI? (USA — May 2025 Refresh)

**Topic**: AI / Careers / Geography / Original Data Analysis / Year-Over-Year
**Format**: 6 slides, 5-6 minute recording
**Audience**: AI/tech professionals considering relocation, career-switchers, students
**Status**: TEMPLATE — fill in placeholders after May 15, 2026 BLS release using `data/usa_yoy_findings.md`

---

## TEMPLATE NOTES

This is the May 15+ refresh template. The original USA video used May 2024 BLS data. This version uses May 2025 data and weaves in year-over-year tidbits per Edward's note: "the fastest growing area over the last year is XYZ" or "shockingly, the location ABC has fallen out of the top 10."

Placeholders to fill in after May 15:
- `{{TOP_METRO_BY_CONC}}` — top metro by concentration in May 2025 (probably still San Jose)
- `{{TOP_METRO_CONC_VAL}}` — its concentration value (currently 7.72)
- `{{NUM_1_ABS}}` — #1 metro by absolute count (currently NY at 21,240)
- `{{NUM_1_ABS_VAL}}` — its absolute count
- `{{FASTEST_GROWER_METRO}}` — fastest-growing metro YoY by percentage
- `{{FASTEST_GROWER_PCT}}` — its YoY percentage growth
- `{{BIGGEST_GAINER_METRO}}` — biggest absolute YoY gainer
- `{{BIGGEST_GAINER_DELTA}}` — its absolute worker delta
- `{{FALLEN_OUT_METRO}}` — any metro that fell out of the top 10 (or "none did")
- `{{NEW_TOP_10_METRO}}` — any metro that newly entered the top 10 (or "none did")
- `{{LEX_PARK_2025_VAL}}` — Lexington Park 2025 concentration (was 6.98 in 2024)
- `{{HUNTSVILLE_2025_VAL}}` — Huntsville 2025 concentration (was 4.30 in 2024)

---

## Slide 1: The Question

**Headline**: Where are the AI jobs in the USA?

**Visual**: A weathered American road map laid flat on a dark wood desk with a single bright blue pin pushed into an unidentified central location, dramatic chiaroscuro lighting, deep shadows, cinematic editorial photograph, no text or visible state names

**Speaker Notes**:
It's Edward Roske and I'm asking good questions. Where are the AI jobs in the USA?

I ran this analysis last week using the Bureau of Labor Statistics data through May 2024, and last Friday BLS dropped the May 2025 release. New data, fresh look. (My excitement about a federal data release is the kind of thing my wife Dawn politely tolerates while not making eye contact.)

Same two SOC codes as last time: 15-1221, Computer and Information Research Scientists, and 15-2051, Data Scientists. Same Metropolitan Statistical Area aggregation. Same code, new file. The picture changed in places I did not expect.

---

## Slide 2: The Data

**Headline**: How I pulled the data, in case you want to check my work.

**Visual**: A cinematic close-up of a terminal screen showing rows of CSV data scrolling past with a code editor open beside it, deep blue glow against pitch black background, magazine-cover composition, no specific text legible

**Speaker Notes**:
BLS publishes a 38-megabyte zip file every May with the prior year's metro-level employment for every Standard Occupational Classification code. Same script as last time. The fetcher tries May 2025 first and falls back to May 2024 if the new release isn't out yet. Last Friday May 2025 went live, so the pipeline picked it up automatically.

Two ways to look at the data: absolute employment and concentration per thousand jobs. Both numbers tell different stories. The year-over-year delta tells a third story. (Most ranking articles publish once and pretend the world is static. The world isn't static.)

Code, raw data, and methodology are at github.com/ERoske/where-is-ai. If a number is wrong, file an issue.

---

## Slide 3: The Big Picture

**Headline**: The map looks different than the headlines.

**Visual**: outputs/Generated Images/Heatmap-USA-AI-Jobs.png

**Speaker Notes**:
By absolute count, {{NUM_1_ABS}} leads with {{NUM_1_ABS_VAL}} working AI professionals. Washington DC, San Francisco-Oakland, Los Angeles, Boston, Dallas, San Jose, and Seattle round out the top eight, each with thousands of AI workers.

By concentration, {{TOP_METRO_BY_CONC}} dominates at {{TOP_METRO_CONC_VAL}} per thousand jobs. The Bay Area splits across two BLS metros (San Francisco-Oakland and San Jose-Sunnyvale-Santa Clara) which together top 20,000 AI workers, putting the actual Bay Area neck-and-neck with New York.

Then the surprise. The top 20 by concentration includes places that aren't supposed to be on this list: Lexington Park Maryland (Pax River), Huntsville Alabama (Redstone Arsenal), Bloomington Illinois, Durham North Carolina, Boulder Colorado, and Provo Utah. Defense and research-anchored AI clusters are real and underreported.

---

## Slide 4: What Changed Year Over Year

**Headline**: Some metros grew faster than the headlines suggested.

**Visual**: A side-by-side cinematic comparison of two map dots with one significantly larger than the other, dramatic moody color contrast, deep blue tones with one gold and one silver dot, magazine-cover editorial photograph, no text

**Speaker Notes**:
The fastest-growing AI metro year-over-year is {{FASTEST_GROWER_METRO}}, up {{FASTEST_GROWER_PCT}} percent from May 2024 to May 2025. The biggest absolute gainer is {{BIGGEST_GAINER_METRO}}, adding {{BIGGEST_GAINER_DELTA}} AI workers in twelve months. (My older son once asked me whether I was excited about a percentage. I said yes. He left the room.)

The harder question is who fell off. {{FALLEN_OUT_METRO}} dropped out of the top 10 by absolute count this year. {{NEW_TOP_10_METRO}} took the slot. The top of the list is not as fixed as people assume.

Lexington Park Maryland is still in the top concentration tier at {{LEX_PARK_2025_VAL}} per thousand jobs, second only to San Jose. Huntsville is still up there at {{HUNTSVILLE_2025_VAL}}. The defense AI cluster I flagged a year ago has not gone anywhere. Most rankings still don't include them.

---

## Slide 5: Concentration vs. Volume

**Headline**: The bigger city wins on options. The denser city wins on culture.

**Visual**: A split-frame composition with the New York skyline at dusk on the left and a quiet Silicon Valley office park at dusk on the right, dramatic warm-cool color contrast, cinematic editorial photograph, no text

**Speaker Notes**:
New York and San Jose are both 'big AI cities' but they buy you different things. New York gives you optionality. If your AI startup fails, the next thirty employers are a subway ride away in finance, media, ads, healthcare, or government. San Jose gives you immersion. Every coffee shop conversation is somebody else's AI startup.

(I once lived in a city where the conference talk was the conversation, which is great for working and terrible for sitting still.) Cost-of-living matters too. Effective compensation in Austin can run thirty percent ahead of San Francisco once you adjust for housing and taxes, which is the real prestige number when nobody is watching.

---

## Slide 6: The Take and What's Next

**Headline**: Pick the lane first. The city follows.

**Visual**: A long winding road through an unidentified American landscape stretching toward a glowing horizon at dusk, deep amber and navy tones, cinematic moody photograph, no signs or markers

**Speaker Notes**:
There are five viable AI lanes in America right now. Frontier labs concentrated in San Francisco and Boston. Federal and defense AI in the DMV, Huntsville, Lexington Park, and Colorado Springs. Robotics in Pittsburgh and Detroit. Enterprise and applied AI in Dallas, Atlanta, and Seattle. Bioinformatics and pharma AI in Boston and Durham.

Pick the lane first. The city follows. (People end up in the wrong city for the right job because they confuse the two.) The map I built doesn't tell you where to live. It tells you which cities have the gravity to make your career easier and which ones don't.

The repo is updated. Same URL, fresh numbers. github.com/ERoske/where-is-ai. If your home town isn't on this map, ask whether you can do the work you want from there or whether you need to move. What does the next ten years of AI look like from the city you actually live in? Until next time, keep asking good questions.

---

## Research Notes

- **Primary data**: BLS OEWS, May 2025 release (Friday May 15, 2026). SOC 15-1221 + 15-2051. Aggregated to MSA. Year-over-year diff vs May 2024.
- **Findings file**: https://github.com/ERoske/where-is-ai/blob/main/data/usa_yoy_findings.md
- **Heatmap**: https://github.com/ERoske/where-is-ai/blob/main/images/Heatmap-USA-AI-Jobs.png

---

## Social Media & YouTube — TEMPLATES (fill in placeholders)

### YouTube
**Title Options** (for A/B/C testing):
1. Where are the AI jobs in the USA in 2025?
2. {{FASTEST_GROWER_METRO}} just became the fastest-growing AI metro in America
3. The 2025 BLS data is out. Here's what changed for AI jobs.

**Description**:
Last week BLS dropped the May 2025 OEWS data. I pulled it the morning it landed, ran the same pipeline I built last year, and computed the year-over-year delta. {{FASTEST_GROWER_METRO}} is the fastest-growing AI metro at {{FASTEST_GROWER_PCT}} percent. {{BIGGEST_GAINER_METRO}} added the most workers in absolute terms ({{BIGGEST_GAINER_DELTA}}). {{FALLEN_OUT_METRO}} dropped out of the top 10. All code, data, and methodology: github.com/ERoske/where-is-ai

#AI #AskingGoodQuestions #AIJobs #DataScience #FutureOfWork

### Twitter/X Post
The 2025 BLS data is out. {{FASTEST_GROWER_METRO}} is the fastest-growing AI metro in America at {{FASTEST_GROWER_PCT}} percent year-over-year. {{BIGGEST_GAINER_METRO}} added {{BIGGEST_GAINER_DELTA}} AI workers. {{FALLEN_OUT_METRO}} fell out of the top 10. Full breakdown: github.com/ERoske/where-is-ai

### LinkedIn Post
The May 2025 BLS data dropped Friday. Here's what changed.

I built this AI hub analysis a week ago using the May 2024 release. The May 2025 OEWS file went live last Friday at 10am ET. I re-ran the same pipeline and computed the year-over-year delta.

Top finding: {{FASTEST_GROWER_METRO}} is the fastest-growing AI metro in America at {{FASTEST_GROWER_PCT}} percent year-over-year. {{BIGGEST_GAINER_METRO}} added {{BIGGEST_GAINER_DELTA}} AI workers in absolute terms — the biggest single-metro gain in the country.

The top of the list shifted. {{FALLEN_OUT_METRO}} dropped out of the top 10 by absolute count. {{NEW_TOP_10_METRO}} took the slot.

The defense AI clusters I flagged last year held their ground. Lexington Park Maryland still sits second only to San Jose on concentration. Huntsville is still in the top 10 on density.

All code, raw data, and methodology: github.com/ERoske/where-is-ai

What does the next ten years of AI look like from the city you actually live in?

#AI #AskingGoodQuestions #AIJobs #DataScience #FutureOfWork
