---
name: native-image-generation
description: Generate images using the agent's internal `generate_image` tool (powered by Gemini/Imagen). Use this for creating assets, mockups, and visual content without external SDK dependencies.
---

# Native Image Generation Skill

This skill documents how to use the agent's native image generation capabilities.

## Skill Location
`{project_path}/skills/native-image-generation`

## Overview
The agent has a built-in `generate_image` tool that uses Google's Imagen model. This allows for zero-setup image generation directly within the chat context or for project assets.

## When to Use
- **Asset Creation**: Generating placeholder images, icons, or background assets for the app.
- **UI Mockups**: Visualizing design concepts.
- **No-Code Generation**: When you want an image *now* without writing a script to call an API.

## Usage Guide (For Agent)

When the user asks for an image, usage of the `z-ai` SDK is **optional**. You can prioritize using the `generate_image` tool for immediate results.

### Tool: `generate_image`

**Parameters:**
- `Prompt`: Detailed text description of the image.
- `ImageName`: Output filename (without extension).

### Best Practices for Prompts
- **Subject**: Clearly define the main subject.
- **Style**: Specify the artistic style (e.g., "cyberpunk", "minimalist", "oil painting", "photorealistic").
- **Lighting**: "Sunset", "studio lighting", "neon", "soft daylight".
- **Quality Keywords**: "4k", "high quality", "detailed", "sharp focus".

**Example Prompt:**
> "A modern dashboard UI mockup for an employee management app, dark mode, vibrant blue accents, clean typography, high quality, 4k"

## generated vs SDK
| Feature | Native Tool (`generate_image`) | External SDK (`z-ai`) |
| :--- | :--- | :--- |
| **Setup** | Zero (Built-in) | Requires API Key & Config |
| **Execution** | Agent-side (Immediate) | Client-side or Script-based |
| **Use Case** | Prototyping, Assets, One-offs | User-facing App Features |

## Workflow
1. User requests image.
2. Agent refines prompt for aesthetics.
3. Agent calls `generate_image`.
4. Agent saves result to artifacts or specific project path.
