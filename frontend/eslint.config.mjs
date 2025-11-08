import { dirname } from "path";
import { fileURLToPath } from "url";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const eslintConfig = [
  ...compat.extends("next/core-web-vitals", "next/typescript"),
  {
    // 为旧文件暂时禁用严格的 TypeScript 规则
    files: [
      "**/hooks/useWebSocket.ts",
      "**/components/trading/**/*.tsx",
      "**/app/virtual-market/**/*.tsx",
      "**/hooks/useScrollSnap.ts",
      "**/app/learn/**/*.tsx"
    ],
    rules: {
      "@typescript-eslint/no-explicit-any": "warn",  // 改为警告而不是错误
      "prefer-const": "warn"  // 改为警告
    }
  }
];

export default eslintConfig;
