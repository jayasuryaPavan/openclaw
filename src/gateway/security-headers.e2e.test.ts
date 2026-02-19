import { describe, expect, it } from "vitest";
import { startGatewayServer } from "./server.js";
import { getFreeGatewayPort } from "./test-helpers.e2e.js";

describe("gateway security headers", () => {
  it("sets security headers on http responses", async () => {
    const port = await getFreeGatewayPort();
    const token = "test-token";
    const server = await startGatewayServer(port, {
      bind: "loopback",
      controlUiEnabled: false,
      auth: { mode: "token", token },
    });

    try {
      const res = await fetch(`http://127.0.0.1:${port}/`);

      expect(res.headers.get("x-content-type-options")).toBe("nosniff");
      expect(res.headers.get("x-frame-options")).toBe("DENY");
      expect(res.headers.get("referrer-policy")).toBe("no-referrer");
    } finally {
      await server.close();
    }
  });
});
