# Course videos: what they showed

Source: four course recordings supplied with the assignment (frames sampled every 15 s and read; no audio transcript). They define the reference app, the PRD workflow and the verification loop this repo follows.

## Module 13, lesson 1 - the reference product (testimonial.to)
A walkthrough of **testimonial.to**, which the capstone recreates in a minimal form:
- **Owner flow**: sign up, a short "how did you hear about us" survey, an empty dashboard (Total videos 0/2, Total spaces, Current plan Free with an Upgrade button), then **Create a new Space**.
- **Space form** tabs: Basic, Prompts, Thank-you page, Extra settings, Notifications. Basic fields: space name (public URL `testimonial.to/<slug>` generated from it), logo (square option), header title, custom message (Markdown), "collect extra information" (name and email on and required; title/company, social link, address optional; up to 5 custom fields), collection type (text, video, or both), star ratings toggle, theme, button colour (paid), language (auto-translate paid). A live preview updates as the form changes.
- **After creation**: a confirmation with the customer access link (Copy / Visit), then the dashboard.
- **Public collection page** at the slug: logo, header title, message, default questions, "Record a video" and "Send in text".
- **Text testimonial modal**: star rating, text, optional images, name, email, title and company, photo, consent checkbox ("I give permission to use this testimonial across social channels and other marketing efforts"), Send; then a thank-you modal.
- Marketing tabs (NPS, case studies, brand monitor, email assistant) were shown but not demonstrated.

## Module 13, lesson 3 - the PRD, written with ChatGPT
The instructor dictated a brief by voice and had ChatGPT turn it into a markdown PRD "that we can hand over to an AI coding agent":
- Brief: a very minimal version; anyone can create an account; from the dashboard create spaces; a space has title and subtitle; configurable fields (name and email required by default, plus company name, social links, profile photo, each toggleable as required); a choice of predefined themes; an inbox of submissions; billing with a Free and a paid plan, Stripe Checkout, success message, webhooks, "already subscribed" state on return; a dashboard upgrade bar on the free plan.
- Resulting PRD sections: product overview; recommended stack (Laravel, Inertia + React, Tailwind and shadcn/ui, MySQL, Cashier, Recharts, queues, Pest); roles (account owner, respondent); authentication; dashboard (stats, collection graph with 7/30/90-day ranges, dismissible upgrade banner); spaces and inbox (review, edit, favorite, hide, publish, delete); embeds ("wall of love") with layout and theme options; plan limits (downgrade never deletes data); billing (the redirect alone is never proof of payment, verify server-side); data model; security (owner-only access, non-guessable public ids, server-side validation, escaped content, rate limits, verified Stripe webhooks, no respondent emails in embeds, UTC); notifications; out of scope (video/audio, custom respondent fields, teams, custom domains, API, integrations, import, AI editing, multiple paid plans, localization); definition of done.
- This repo's `docs/prd.md` is the trimmed version of that PRD.

## Module 4, lesson 5 - Phase 03: Verify
Slide: "Machine first. Then a fresh pair of eyes." Automated checks (tests green, static analysis clean, lint correct, every file in the diff appears in `plan.md`), then a **fresh critic subagent** reviews the diff against the plan and answers "Approved". Demo on a Laravel call-statistics app: a separate Claude session reads `plan.md`, runs `git diff`, the test suite and Pint, reports deviations and minor notes, and ends with "Approved"; the implementation session then builds assets, commits and pushes. Exercise 03: run one tiny change through the full plan, implement, verify loop with `brief.md` and `plan.md` written in Plan Mode before any writes. This repo's `critic` agent and `verify-feature` skill implement that loop.

## Module 13, lesson 8 - parallel work with Conductor
Conductor creates an isolated workspace (a git worktree copy, named after a city) from `origin/main`, detects a setup script (composer install), and a run script starts the app and Vite on workspace-specific ports. The repo carries tool config folders (`.claude`, `.codex`, `.cursor`, `.conductor`, `.context`). This repo does the same with git worktrees: the embed wall and dashboard were built on a separate branch and merged with `--no-ff`.
