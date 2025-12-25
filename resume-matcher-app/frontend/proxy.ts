import nextAuthMiddleware from "next-auth/middleware";
import type { NextRequest } from "next/server";
import type { NextRequestWithAuth } from "next-auth/middleware";

export function proxy(req: NextRequest) {
  return nextAuthMiddleware(req as NextRequestWithAuth);
}

export const config = {
  matcher: ["/history"],
};
