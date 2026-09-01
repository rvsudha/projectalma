"use client";

import { clsx } from "clsx";
import { useId, useRef, useState } from "react";

import { formatBytes } from "@/lib/format";

import { FileText, Upload, X } from "./Icons";
import { FieldShell } from "./Field";
import styles from "./FileDropzone.module.css";

interface Props {
  label: string;
  hint?: string;
  accept?: string;
  error?: string;
  value?: File | null;
  onChange: (file: File | null) => void;
}

export function FileDropzone({ label, hint, accept, error, value, onChange }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const id = useId();
  const [dragging, setDragging] = useState(false);

  function open() {
    inputRef.current?.click();
  }

  return (
    <FieldShell id={id} label={label} hint={hint} error={error}>
      <input
        ref={inputRef}
        id={id}
        type="file"
        accept={accept}
        className={styles.input}
        tabIndex={-1}
        onChange={(e) => onChange(e.target.files?.[0] ?? null)}
      />

      {value ? (
        <div className={styles.selected}>
          <FileText width={22} height={22} className={styles.selectedIcon} />
          <div className={styles.selectedMeta}>
            <div className={styles.selectedName}>{value.name}</div>
            <div className={styles.selectedSize}>{formatBytes(value.size)}</div>
          </div>
          <button
            type="button"
            className={styles.remove}
            aria-label="Remove file"
            onClick={() => {
              onChange(null);
              if (inputRef.current) inputRef.current.value = "";
            }}
          >
            <X width={16} height={16} />
          </button>
        </div>
      ) : (
        <div
          role="button"
          tabIndex={0}
          aria-describedby={hint ? `${id}-hint` : undefined}
          className={clsx(
            styles.zone,
            dragging && styles.dragging,
            error && styles.invalid,
          )}
          onClick={open}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              open();
            }
          }}
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragging(false);
            const file = e.dataTransfer.files?.[0];
            if (file) onChange(file);
          }}
        >
          <Upload width={22} height={22} className={styles.icon} />
          <span className={styles.primary}>
            Drag a file here, or <span className={styles.link}>browse</span>
          </span>
          <span className={styles.hint}>PDF, DOC or DOCX · up to 10&nbsp;MB</span>
        </div>
      )}
    </FieldShell>
  );
}
