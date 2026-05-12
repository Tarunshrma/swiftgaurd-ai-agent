# SWIFT Transaction Processing System - Starter Code

## Project Structure

This starter code has been scaffolded to help you focus on implementing the 15 TODOs across the project. The directory structure mirrors the solution, with all necessary files in place.

```
project/
├── agents/                      # Agent pattern implementations
│   ├── evaluator_optimizer.py   # Complete (no TODOs)
│   ├── orchestrator_worker.py   # TODO 15: Orchestrator implementation
│   ├── parallelization.py       # TODOs 10-12: Parallel fraud detection
│   ├── prompt_chaining.py       # TODOs 13-14: Chain of agents
│   └── workflow_agents/
│       └── base_agents.py       # TODOs 6-9: Base agent architecture
├── models/                       # Data models (Complete)
│   ├── bank.py                  # Bank entity
│   └── swift_message.py         # SWIFT message structure
├── services/                     # Utility services (Complete)
│   ├── llm_service.py           # OpenAI integration
│   └── swift_generator.py       # Message generation
├── config.py                     # Configuration settings
├── main.py                       # TODOs 1-5: Main integration
└── generate_swift_messages.py   # Standalone message generator
```

## TODO Implementation Guide

### Getting Started

1. **Set up your environment:**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   pip install faker numpy openai pandas pydantic scipy
   ```

2. **Start with TODOs 1-5 in main.py:**
   These are simple method calls that help you understand the flow.

3. **Move to TODOs 6-9 in base_agents.py:**
   Create the base agent architecture that other agents will use.

4. **Complete TODOs 10-12 in parallelization.py:**
   Add a third fraud agent and implement aggregation.

5. **Implement TODOs 13-14 in prompt_chaining.py:**
   Complete the chain of specialized agents.

6. **Finish with TODO 15 in orchestrator_worker.py:**
   This is the most complex TODO - create the full orchestrator-worker pattern.

## TODO Locations and Points

| TODO | File | Line | Points | Description |
|------|------|------|--------|-------------|
| 1 | main.py | ~155 | 5 | Call evaluator optimizer |
| 2 | main.py | ~167 | 5 | Call parallelization |
| 3 | main.py | ~178 | 5 | Call prompt chaining |
| 4 | main.py | ~189 | 5 | Pass to orchestrator |
| 5 | main.py | ~98 | 5 | Modify filtering logic |
| 6 | base_agents.py | ~8 | 10 | Create BaseAgent class |
| 7 | base_agents.py | ~47 | 5 | Initialize LLMService |
| 8 | base_agents.py | ~81 | 3 | Set response format |
| 9 | base_agents.py | ~91 | 2 | Parse JSON response |
| 10 | parallelization.py | ~33 | 10 | Add third fraud agent |
| 11 | parallelization.py | ~69 | 5 | Create aggregator |
| 12 | parallelization.py | ~127 | 5 | Mark fraudulent |
| 13 | prompt_chaining.py | ~185 | 7 | Technical analyst |
| 14 | prompt_chaining.py | ~204 | 8 | Compliance officer |
| 15 | orchestrator_worker.py | ~26 | 15 | Full orchestrator |

## Testing Your Implementation

### Test Individual Components

Each file has a test method at the bottom:

```bash
# Test base agents
python agents/workflow_agents/base_agents.py

# Test parallelization
python agents/parallelization.py

# Test prompt chaining (requires API key)
python agents/prompt_chaining.py

# Test evaluator optimizer
python agents/evaluator_optimizer.py

# Test orchestrator (requires API key)
python agents/orchestrator_worker.py
```

### Run the Complete System

Once all TODOs are implemented:

```bash
python main.py
```

## Helpful Hints

### For TODO 6 (BaseAgent):
- Use `from abc import ABC, abstractmethod`
- The BaseAgent should have methods that all agents share
- Look at the provided agent classes (FraudAmountDetectionAgent, etc.) for patterns

### For TODO 10 (Third Agent):
Ideas for your third fraud detection agent:
- **BenfordLawAgent**: Check if amounts follow Benford's Law distribution
- **VelocityCheckAgent**: Detect rapid succession of transactions
- **GeographicRiskAgent**: Assess country-based risk levels
- **TimeBasedRiskAgent**: Flag transactions at unusual hours

### For TODO 15 (Orchestrator):
This is the most complex TODO. Break it down:
1. First, create the Orchestrator class that analyzes messages
2. Then, create the GenericAgent class that executes tasks
3. Finally, implement the process_with_orchestrator method to coordinate them

### Common Issues and Solutions

**Import Errors:**
- Ensure all __init__.py files exist
- Check that you're importing from the correct paths

**OpenAI API Errors:**
- Verify your API key is set: `echo $OPENAI_API_KEY`
- Check you have API credits available
- Ensure you're using the correct model name ("gpt-4o")

**JSON Parsing Errors:**
- Always include `response_format={"type": "json_object"}` in OpenAI calls
- Use try-except blocks when parsing JSON responses

## Submission Requirements

1. **Complete all 15 TODOs**
2. **Generate two different report sets** (TODO 5):
   - Run 1: Default non-fraudulent messages
   - Run 2: Modified filter (e.g., fraudulent only, high-value, specific type)
3. **Include console output** showing both runs
4. **Document your third fraud agent** (TODO 10)

## Need Help?

1. Review the lesson solutions for examples of each pattern
2. Check the provided agent classes for implementation patterns
3. Use the test methods in each file to debug
4. Look at the detailed instructions in each TODO comment

Good luck with your implementation!