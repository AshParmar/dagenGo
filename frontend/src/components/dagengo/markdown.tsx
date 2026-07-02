import { useMemo, type ReactNode } from "react";

export function Markdown({ source }: { source: string }) {
  const blocks = useMemo(() => parseBlocks(source), [source]);
  return <div>{blocks}</div>;
}

function parseBlocks(md: string): ReactNode[] {
  const lines = md.split("\n");
  const out: ReactNode[] = [];
  let i = 0;
  let key = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (line.startsWith("```")) {
      const lang = line.slice(3).trim();
      const code: string[] = [];
      i++;
      while (i < lines.length && !lines[i].startsWith("```")) {
        code.push(lines[i]);
        i++;
      }
      i++;
      out.push(
        <pre
          key={key++}
          className="my-4 overflow-x-auto rounded-lg border border-border bg-surface p-4 text-[13px] font-mono leading-relaxed text-foreground/90"
        >
          {lang && (
            <div className="mb-2 text-xs uppercase tracking-wide text-muted-foreground">{lang}</div>
          )}
          <code>{code.join("\n")}</code>
        </pre>,
      );
      continue;
    }
    if (/^#{1,4}\s/.test(line)) {
      const level = line.match(/^#+/)![0].length;
      const text = line.replace(/^#+\s/, "");
      const sizes = ["text-2xl", "text-xl", "text-lg", "text-base"];
      out.push(
        <div key={key++} className={`mt-6 mb-3 font-semibold tracking-tight ${sizes[level - 1]}`}>
          {inline(text)}
        </div>,
      );
      i++;
      continue;
    }
    if (line.startsWith("> ")) {
      const quote: string[] = [];
      while (i < lines.length && lines[i].startsWith("> ")) {
        quote.push(lines[i].slice(2));
        i++;
      }
      out.push(
        <blockquote
          key={key++}
          className="my-4 border-l-2 border-primary/60 pl-4 italic text-muted-foreground"
        >
          {inline(quote.join(" "))}
        </blockquote>,
      );
      continue;
    }
    if (line.startsWith("|") && lines[i + 1]?.includes("---")) {
      const header = splitRow(line);
      i += 2;
      const rows: string[][] = [];
      while (i < lines.length && lines[i].startsWith("|")) {
        rows.push(splitRow(lines[i]));
        i++;
      }
      out.push(
        <div key={key++} className="my-4 overflow-x-auto rounded-lg border border-border">
          <table className="w-full text-sm">
            <thead className="bg-surface text-left text-xs uppercase tracking-wide text-muted-foreground">
              <tr>
                {header.map((c, j) => (
                  <th key={j} className="px-4 py-2 font-medium">
                    {inline(c)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((r, ri) => (
                <tr key={ri} className="border-t border-border">
                  {r.map((c, j) => (
                    <td key={j} className="px-4 py-2 align-top">
                      {inline(c)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>,
      );
      continue;
    }
    if (/^[-*]\s/.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^[-*]\s/.test(lines[i])) {
        items.push(lines[i].replace(/^[-*]\s/, ""));
        i++;
      }
      out.push(
        <ul key={key++} className="my-3 list-disc space-y-1 pl-6 text-[15px] text-foreground/90">
          {items.map((it, j) => (
            <li key={j}>{inline(it)}</li>
          ))}
        </ul>,
      );
      continue;
    }
    if (line.trim() === "") {
      i++;
      continue;
    }
    const para: string[] = [];
    para.push(lines[i]);
    i++;
    while (i < lines.length && lines[i].trim() !== "" && !/^(```|#{1,4}\s|> |\||[-*]\s)/.test(lines[i])) {
      para.push(lines[i]);
      i++;
    }
    out.push(
      <p key={key++} className="my-3 text-[15px] leading-7 text-foreground/90">
        {inline(para.join(" "))}
      </p>,
    );
  }
  return out;
}

function splitRow(line: string): string[] {
  return line
    .split("|")
    .slice(1, -1)
    .map((c) => c.trim());
}

function inline(text: string): ReactNode {
  const parts: ReactNode[] = [];
  let rest = text;
  let k = 0;
  const re = /(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*)/;
  while (true) {
    const m = rest.match(re);
    if (!m) {
      parts.push(rest);
      break;
    }
    const idx = m.index!;
    if (idx > 0) parts.push(rest.slice(0, idx));
    const token = m[0];
    if (token.startsWith("`"))
      parts.push(
        <code
          key={k++}
          className="rounded bg-surface px-1.5 py-0.5 font-mono text-[13px] text-primary"
        >
          {token.slice(1, -1)}
        </code>,
      );
    else if (token.startsWith("**"))
      parts.push(
        <strong key={k++} className="font-semibold text-foreground">
          {token.slice(2, -2)}
        </strong>,
      );
    else
      parts.push(
        <em key={k++} className="italic text-foreground/95">
          {token.slice(1, -1)}
        </em>,
      );
    rest = rest.slice(idx + token.length);
  }
  return <>{parts}</>;
}
