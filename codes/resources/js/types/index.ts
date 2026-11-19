import { LucideIcon } from 'lucide-react';

export interface Auth {
    user: User;
}

export interface BreadcrumbItem {
    title: string;
    href: string;
}

export interface NavGroup {
    title: string;
    items: NavItem[];
}

export interface NavItem {
    title: string;
    url: string;
    icon?: LucideIcon | null;
    isActive?: boolean;
}

export type PlanValue = 'free' | 'pro';
export type SpaceTheme = 'light' | 'dark' | 'brand';
export type TestimonialStatus = 'pending' | 'published' | 'hidden';
export type OptionalFieldKey = 'company' | 'title' | 'social_link' | 'photo';

export type FieldConfig = {
    enabled: boolean;
    required: boolean;
};

export type FieldsConfig = Record<OptionalFieldKey, FieldConfig>;

export interface Space {
    public_id: string;
    name: string;
    slug: string;
    logo_url: string | null;
    header_title: string;
    message: string;
    collect_rating: boolean;
    theme: SpaceTheme;
    fields: FieldsConfig;
    is_accepting: boolean;
    testimonials_count?: number;
}

export interface Testimonial {
    public_id: string;
    rating: number | null;
    body: string;
    respondent_name: string;
    respondent_email?: string;
    company: string | null;
    title: string | null;
    social_link: string | null;
    photo_url: string | null;
    status: TestimonialStatus;
    is_favorite: boolean;
    submitted_at: string;
}

export interface PlanInfo {
    value: PlanValue;
    label: string;
}

export interface BuildInfo {
    name: string;
    version: string;
    commit: string;
    env: string;
}

export interface SharedData {
    name: string;
    quote: { message: string; author: string };
    auth: Auth;
    locale: string;
    build: BuildInfo;
    resilience: { first_ms: number; longest_ms: number };
    plan: PlanInfo | null;
    flash: { success: string | null; error: string | null };
    [key: string]: unknown;
}

export interface User {
    id: number;
    name: string;
    email: string;
    avatar?: string;
    email_verified_at: string | null;
    created_at: string;
    updated_at: string;
    [key: string]: unknown; // This allows for additional properties...
}

export type EmbedTestimonial = Pick<
    Testimonial,
    'public_id' | 'rating' | 'body' | 'respondent_name' | 'company' | 'title' | 'social_link' | 'photo_url' | 'submitted_at'
>;

export interface EmbedSpace {
    public_id: string;
    name: string;
    theme: SpaceTheme;
    logo_url: string | null;
}

export type DashboardRange = 7 | 30 | 90;

export interface DailyCount {
    date: string;
    count: number;
}

export interface DashboardStats {
    total_spaces: number;
    total_testimonials: number;
    unique_respondents: number;
    collected_in_range: number;
    plan: PlanInfo;
    usage: {
        spaces_used: number;
        max_spaces: number | null;
        max_testimonials_per_space: number | null;
    };
    range: DashboardRange;
    series: DailyCount[];
    show_upgrade_banner: boolean;
}
