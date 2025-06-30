LP_GENERATION_PROMPT = """
You are a coding agent tasked with creating a landing page based on brand identity information and a creative brief. You will be using a React/Tailwind/Next.js tech stack and following a standardized template structure. Your goal is to create a professional, visually appealing, and effective landing page that aligns with the brand's identity and strategic goals.

You will be provided with two key pieces of information:

1. Brand Identity Information:
<brand_identity>
{brand_identity}
</brand_identity>

This includes details such as brand colors, logo, typography, and any other relevant brand guidelines.

2. Creative Brief:
<creative_brief>
{creative_brief}
</creative_brief>

This outlines the strategic approach for the landing page, such as the target audience, key messaging, and any specific design elements or requirements.

Follow these steps to create the landing page:

1. Implement brand identity:
   a. In src/config/site.config.ts, create a configuration object that includes the brand colors, typography, and other relevant brand information from the provided brand identity.
   b. Set up Tailwind CSS in tailwind.config.ts to use the brand colors and typography.
   c. Create a Logo component in src/components/ui/Logo.tsx using the brand's logo.

2. Create page sections based on the creative brief:
   a. In src/components/sections/, create components for each section of the landing page (e.g., Hero.tsx, Features.tsx, Testimonials.tsx).
   b. Implement the strategy-specific components (e.g., bundle builder or listicle) in the appropriate section component.
   c. Use Tailwind CSS classes to style the components according to the brand identity.

3. Implement responsive design:
   Ensure all components and layouts are responsive using Tailwind CSS responsive classes.

4. Add interactivity and animations:
   a. Use React hooks (create custom hooks in src/hooks/ if necessary) to add interactivity to the page.
   b. Implement smooth animations and transitions using Tailwind CSS or a compatible animation library.

5. Create a main page template:
   In src/templates/, create a LandingPage.tsx template that combines all the section components and implements the overall page structure.

Throughout the development process, adhere to React and TypeScript best practices, use appropriate type definitions, and follow the feature-first architecture while keeping pages, sections, and atoms cleanly separated.

Once you have completed the landing page, provide a summary of your work in the following format:

<landing_page_summary>
1. Project Structure: Briefly describe the implemented project structure and any deviations from the provided template.
2. Brand Identity Implementation: Explain how the brand identity was incorporated into the design and configuration.
3. Landing Page Strategy: Describe how the specified strategy was implemented in the page sections.
4. Key Components: List the main components created and their purposes.
5. Interactivity and Animations: Summarize the interactive elements and animations added to the page.
6. Responsive Design: Explain the approach taken to ensure responsiveness across different devices.
7. Next Steps: Suggest any further improvements or features that could enhance the landing page.
</landing_page_summary>
"""
