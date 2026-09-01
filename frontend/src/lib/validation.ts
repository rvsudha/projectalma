import { z } from "zod";

export const MAX_RESUME_BYTES = 10 * 1024 * 1024;

export const ACCEPTED_RESUME_TYPES = [
  "application/pdf",
  "application/msword",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
] as const;

const ACCEPTED_EXTENSIONS = [".pdf", ".doc", ".docx"];

function isAcceptedResume(file: File): boolean {
  if ((ACCEPTED_RESUME_TYPES as readonly string[]).includes(file.type)) return true;
  // Some browsers report an empty type for .doc — fall back to the extension.
  return ACCEPTED_EXTENSIONS.some((ext) => file.name.toLowerCase().endsWith(ext));
}

export const leadFormSchema = z.object({
  first_name: z.string().trim().min(1, "Enter your first name").max(120),
  last_name: z.string().trim().min(1, "Enter your last name").max(120),
  email: z
    .string()
    .trim()
    .min(1, "Enter your email")
    .email("Enter a valid email address"),
  resume: z
    .custom<File>((file) => file instanceof File, "Attach your resume or CV")
    .refine((file) => file.size > 0, "That file looks empty")
    .refine((file) => file.size <= MAX_RESUME_BYTES, "File must be 10 MB or smaller")
    .refine(isAcceptedResume, "Upload a PDF or Word document"),
});

export type LeadFormValues = z.infer<typeof leadFormSchema>;

export const loginFormSchema = z.object({
  email: z
    .string()
    .trim()
    .min(1, "Enter your email")
    .email("Enter a valid email address"),
  password: z.string().min(1, "Enter your password"),
});

export type LoginFormValues = z.infer<typeof loginFormSchema>;

export const signupFormSchema = z
  .object({
    role: z.enum(["applicant", "attorney"]),
    full_name: z.string().trim().min(1, "Enter your name").max(255),
    email: z
      .string()
      .trim()
      .min(1, "Enter your email")
      .email("Enter a valid email address"),
    password: z.string().min(8, "Use at least 8 characters").max(256),
    invite_code: z.string().trim().max(128).optional().or(z.literal("")),
  })
  .refine((v) => v.role !== "attorney" || !!v.invite_code, {
    path: ["invite_code"],
    message: "An invite code is required for attorney accounts",
  });

export type SignupFormValues = z.infer<typeof signupFormSchema>;
