# hwanchang-plugins

Claude Code plugin marketplace by hwanchang.

## Installation

### Add Marketplace

```bash
/plugin marketplace add hwanchang/skill-evaluator
```

### Install Plugin

```bash
/plugin install skill-evaluator@hwanchang-plugins
```

## Available Plugins

### skill-evaluator

Forces Claude to explicitly evaluate available skills before responding to any user prompt.

**Features:**
- Automatically scans all installed plugins for available skills
- Displays skill list with descriptions on every user prompt
- Enforces a mandatory 3-step evaluation protocol:
  1. **EVALUATE**: List each skill with YES/NO and brief reason
  2. **ACTIVATE**: Call Skill tool for relevant skills
  3. **IMPLEMENT**: Only proceed after evaluation complete

## For Team Projects

Add to your project's `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "hwanchang-plugins": {
      "source": {
        "source": "github",
        "repo": "hwanchang/skill-evaluator"
      }
    }
  },
  "enabledPlugins": {
    "skill-evaluator@hwanchang-plugins": true
  }
}
```

## Requirements

- Python 3.9+
- Claude Code with plugin support

## License

MIT
