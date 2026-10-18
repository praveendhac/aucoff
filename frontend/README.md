# AUCoFF frontend

Next.js (App Router, TypeScript strict) application. See [`specs/frontend-spec.md`](../specs/frontend-spec.md) and [`specs/design.md`](../specs/design.md).

```
npm install        # install (uses the in-repo sharp stub, see ../LICENCES.md)
npm run dev        # http://localhost:3000
npm run lint && npm run typecheck && npm test && npm run format:check
npm run licences   # licence gate (LIC-1, LIC-2, LIC-5)
```

Image optimisation is disabled on purpose: Next.js's optional `sharp` pulls LGPL libvips, which the constitution disallows (LIC-2).
