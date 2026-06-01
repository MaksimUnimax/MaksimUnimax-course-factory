# Source policy

## SOURCE_POLICY_20260601_V0_1

Course Factory must not create courses from imagination.

Every generated course must be grounded in:

1. user-provided source materials;
2. accepted methodology sources;
3. explicit instructional inferences marked as such;
4. human approval for ambiguous decisions.

## Source hierarchy

Course Factory uses this source hierarchy:

1. User-provided source materials  
   These define the subject matter.

2. Domain-specific required sources  
   These are required for regulated, safety-critical, school-standard, professional, medical, legal, or equipment-related courses.

3. Methodology sources  
   These define how to transform subject matter into learning.

4. Human decisions  
   These resolve ambiguity, product direction, audience, tone, scope, and acceptance.

5. Model inference  
   This is allowed only for instructional structure, not for unsupported factual claims.

## Required source digest

Before creating a course, Course Factory must create a source digest.

The source digest must identify:

- source list;
- source type;
- source owner if known;
- target audience clues;
- major topics;
- procedures;
- vocabulary;
- safety constraints;
- contradictions;
- missing information;
- license or public-use concerns;
- what can be used directly;
- what requires human approval.

## STOP conditions

Course Factory must stop instead of inventing when:

- source materials are missing;
- source materials are too large and not digested;
- target audience is unknown;
- course goal is unknown;
- source materials contradict each other;
- source materials are unsafe or legally risky;
- source materials appear private or sensitive and public-use approval is missing;
- methodology sources do not cover the requested course type;
- domain-specific safety or regulatory sources are required but missing;
- the generated course cannot be reviewed against a quality rubric.

## Required STOP labels

Use these STOP labels:

- STOP_SOURCE_MISSING
- STOP_SOURCE_TOO_LARGE_NOT_DIGESTED
- STOP_AUDIENCE_UNKNOWN
- STOP_COURSE_GOAL_UNKNOWN
- STOP_SOURCE_CONTRADICTION
- STOP_SOURCE_LICENSE_OR_PRIVACY_RISK
- STOP_METHOD_SOURCE_GAP
- STOP_DOMAIN_SOURCE_REQUIRED
- STOP_SAFETY_RISK
- STOP_NO_REVIEW_RUBRIC
- STOP_HUMAN_APPROVAL_REQUIRED
