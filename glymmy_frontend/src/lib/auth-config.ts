const explicitAuthFlag = process.env.NEXT_PUBLIC_ENABLE_AUTH;

export function isAuthEnabledServer() {
  if (explicitAuthFlag === "false") {
    return false;
  }

  return Boolean(
    process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY && process.env.CLERK_SECRET_KEY
  );
}

export function isAuthEnabledClient() {
  if (explicitAuthFlag === "false") {
    return false;
  }

  return Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY);
}
