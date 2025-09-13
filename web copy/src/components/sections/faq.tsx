import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "@/components/ui/accordion";

export default function FAQSection(): JSX.Element {
  return (
    <section className="bg-background py-20">
      <div className="container max-w-5xl mx-auto px-6">
        <h2 className="text-3xl md:text-4xl font-semibold text-foreground mb-8">
          FAQs
        </h2>
        
        <Accordion type="single" collapsible className="w-full">
          <div className="border-t border-border"></div>
          
          <AccordionItem value="item-1" className="border-b border-border">
            <AccordionTrigger className="text-xl md:text-2xl font-semibold text-foreground py-6 hover:no-underline [&[data-state=open]]:text-foreground">
              Why open-core?
            </AccordionTrigger>
            <AccordionContent className="text-body-large text-muted-foreground pb-6">
              Trust. Community. Teams need to audit and extend the local engine (CLI, orchestrator, guardrails, adapters). We monetize the transformational bits—plan/patch/resoning—so we can reinvest in R&D while keeping the core transparent.
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="item-2" className="border-b border-border">
            <AccordionTrigger className="text-xl md:text-2xl font-semibold text-foreground py-6 hover:no-underline [&[data-state=open]]:text-foreground">
              What's the end goal?
            </AccordionTrigger>
            <AccordionContent className="text-body-large text-muted-foreground pb-6">
              A world where the most capable penetration tester is an AI agent that changes how companies identify vulnerabilities
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="item-3" className="border-b border-border">
            <AccordionTrigger className="text-xl md:text-2xl font-semibold text-foreground py-6 hover:no-underline [&[data-state=open]]:text-foreground">
              Why terminal-based?
            </AccordionTrigger>
            <AccordionContent className="text-body-large text-muted-foreground pb-6">
              Security belongs in the developer loop. A CLI is fast, scriptable, auditable, easy to lock down, and integrates cleanly with CI and policy.
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="item-4" className="border-b border-border">
            <AccordionTrigger className="text-xl md:text-2xl font-semibold text-foreground py-6 hover:no-underline [&[data-state=open]]:text-foreground">
              What data do you collect?
            </AccordionTrigger>
            <AccordionContent className="text-body-large text-muted-foreground pb-6">
              ZDR e2e encrypted with blind computation based on pay tier, if not, the data will be used to improve the product.
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </div>
    </section>
  );
}