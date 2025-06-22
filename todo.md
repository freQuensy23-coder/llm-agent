# Contextual Chat Customization System

## **Objective & Importance**

Enable Roam’s AI-powered game builder to dynamically adapt its UI and intelligently auto-tune gameplay parameters based on user intent and game type. This reduces cognitive load for creators, ensures optimal defaults, and creates a collaborative experience where chat drives game creation with real-time feedback and suggestions.

---

## **System Architecture Overview**

- **Chat UI (iOS/SwiftUI):** Primary interface for users to describe and build games via natural language.
- **LLM (Embedded or Remote):** Interprets user input, generates follow-up questions, and suggests game design improvements.
- **Unity Engine (Embedded):** Executes game logic, visualizes the world, and communicates parameter/state changes.
- **Data Schema:** Defines editable parameters for World, Gameplay, and Art Style. Tracks which are set, inferred, or missing.

---

## **Chat-Driven Game Creation Flow**

1. **User enters a prompt**
    
    → *"I want to make a low-gravity shooter in space."*
    
2. **LLM processes context**
    
    → Extracts game type ("Shooter"), modifiers ("low gravity", "space"), inferred setting gaps.
    
3. **Unity executes actions**
    
    → Loads Shooter template, applies low-gravity physics, sets space-themed world, adds basic weapons.
    
4. **LLM follows up**
    
    → *“Should I add AI enemies or will this be PvP?”*
    
    → *“Want to see how weightless the jump feels?”*
    
5. **AI tunes values**
    
    → Based on best practices, LLM applies “smart defaults” dynamically.
    

---

## **Game Creation Aspects & Parameters**

### **1. World**

- Objects, environment type (farm, city, space), time of day, weather, terrain

### **2. Gameplay**

- Abilities, power-ups, player movement, difficulty rules, win conditions

### **3. Art Style**

- Visual theme, shaders, character design, UI/UX aesthetic

If users miss key areas, the LLM either:

- **Auto-fills values** using defaults and context, or
- **Asks intelligent questions** to complete the setup

---

## **Key Functionalities**

### **1. Game Type Classification & UI Adaptation**

- LLM detects game type from prompt
- Unity adapts UI: only relevant parameters are shown
    - *Runner:* Jump Height, Gravity, Coyote Time
    - *Racing:* Turn Speed, Drift, Acceleration
- Non-relevant options hidden by default, surfaced when needed

### **2. Smart Parameter Defaults**

- LLM injects **pre-tested defaults** based on prompt + game type
- Can interpret subjective language:
    - *“I want floaty jumps” → lower gravity, longer hang time*
    - *“Make aiming snappy” → tighter turn speed, shorter delay*

### **3. Continuous Refinement**

- Gameplay sessions tracked for feedback loops
- Adjusts defaults if most users:
    - Fail platforming → increase Coyote Time
    - Crash in corners → reduce Turn Acceleration

### **4. Proactive Clarifications**

- If input is ambiguous or conflicting:
    - *“You set ‘steal a chicken’ in a city setting. Change to farm?”*
- Prevents mismatches and builds coherent worlds

### **5. UI Simplification Without Restriction**

- Essential settings visible by default
- Advanced toggles hidden under expandable menus
- All AI-suggested values are editable by the user

---

## **Technical Feasibility**

- **Feasible with structured schemas** and intelligent prompt parsing
- Requires:
    - Well-defined parameter map per game type
    - Real-time state tracking in Unity
    - Schema exposure to LLM for parameter boundaries and presets

### **Constraints**

- Accurate classification is critical — misjudging game type leads to poor defaults
- NLP model must evolve with edge-case phrasing
- Chat UI must remain responsive and minimal, even as complexity scales

---

## **System Schema Must Include**

- Field: `parameterName`
- Type: `numeric/string/bool`
- Bounds: `min`, `max`, `recommendedRange`
- Game Types: `applicableTo`
- IsSet: `true/false`
- Source: `user/ai/default`

This enables:

- Structured decisions from the LLM
- Real-time adaptability
- Transparent overrides for users