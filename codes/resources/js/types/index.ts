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

export interface SharedData {
    name: string;
    quote: { message: string; author: string };
    auth: Auth;
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
