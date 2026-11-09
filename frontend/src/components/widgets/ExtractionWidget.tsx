import React from 'react';
import { AlertCircle, CheckCircle2, FileText, RefreshCw } from 'lucide-react';
import type { UI } from '../../types';

interface Props {
  ui: UI;
  onSend: (value: any) => void;
  disabled?: boolean;
}

export const ExtractionWidget: React.FC<Props> = ({ ui, onSend, disabled }) => {
  const data = ui.data || {};
  const isMismatch = data.status === 'MISMATCH' || data.status === 'WRONG_TYPE';
  const mismatches = data.mismatches || [];

  const fields = data.extracted_fields || [
    {
      label: 'Patient name',
      value: data.patient_name || 'Kunal Shah',
      subtext: isMismatch ? (mismatches[0] || 'Claim says: Neha Shah') : 'Verified from policy',
      status: isMismatch ? 'warning' : 'ok',
    },
    {
      label: 'Hospital',
      value: data.hospital_name || 'Lilavati Hospital',
      subtext: '"Lilavati Hospital & Research Centre"',
      status: 'ok',
    },
    {
      label: 'Admission date',
      value: data.doa || '24 Sep 2026',
      subtext: '"Date of Admission: 24/09/2026"',
      status: 'ok',
    },
    {
      label: 'Discharge date',
      value: data.dod || '27 Sep 2026',
      subtext: '"Date of Discharge: 27/09/2026"',
      status: 'ok',
    },
    {
      label: 'Final diagnosis',
      value: data.diagnosis || 'Acute appendicitis',
      subtext: '"Diagnosis: Acute Appendicitis"',
      status: 'ok',
    },
    {
      label: 'Treating doctor',
      value: data.doctor_name || 'Could not read clearly',
      subtext: 'confidence 0.42',
      status: 'unclear',
    },
  ];

  return (
    <div
      style={{
        padding: '14px',
        marginTop: '12px',
        borderRadius: '16px',
        backgroundColor: '#FFFFFF',
        border: '1px solid #E2E8F0',
        boxShadow: '0 4px 16px rgba(0, 0, 0, 0.04)',
        width: '100%',
        boxSizing: 'border-box',
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <FileText color="#0052CC" size={18} />
          <span style={{ fontWeight: 700, color: '#1E293B', fontSize: '0.9rem' }}>
            {data.doc_code === 'DISCHARGE_SUMMARY' ? 'Discharge summary' : (data.doc_code || 'Document Verification')}
          </span>
        </div>
        {isMismatch ? (
          <span
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              backgroundColor: '#FEF3C7',
              color: '#92400E',
              fontWeight: 600,
              fontSize: '0.72rem',
              padding: '3px 8px',
              borderRadius: '12px',
              border: '1px solid #FDE68A',
            }}
          >
            <AlertCircle size={13} color="#D97706" />
            {`${mismatches.length || 1} mismatch`}
          </span>
        ) : (
          <span
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              backgroundColor: '#DCFCE7',
              color: '#15803D',
              fontWeight: 600,
              fontSize: '0.72rem',
              padding: '3px 8px',
              borderRadius: '12px',
            }}
          >
            <CheckCircle2 size={13} color="#10B981" />
            Verified
          </span>
        )}
      </div>

      {/* 2-Column Grid Layout matching reference image */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 180px), 1fr))', gap: '10px', marginBottom: '14px' }}>
        {fields.map((field: any, idx: number) => (
          <div
            key={idx}
            style={{
              padding: '8px 10px',
              borderRadius: '12px',
              backgroundColor: '#F8FAFC',
              border: '1px solid #F1F5F9',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'flex-start',
              minHeight: '60px',
            }}
          >
            <div style={{ minWidth: 0, flex: 1 }}>
              <span style={{ fontSize: '0.72rem', color: '#64748B', display: 'block' }}>{field.label}</span>
              <span
                style={{
                  fontWeight: 700,
                  color: field.status === 'unclear' ? '#64748B' : '#1E293B',
                  fontSize: '0.85rem',
                  lineHeight: 1.2,
                  marginTop: '2px',
                  display: 'block',
                  wordBreak: 'break-word',
                }}
              >
                {field.value}
              </span>
              <span style={{ fontStyle: 'italic', color: '#94A3B8', fontSize: '0.68rem', display: 'block', wordBreak: 'break-word' }}>
                {field.subtext}
              </span>
            </div>

            <div style={{ marginLeft: '6px', flexShrink: 0 }}>
              {field.status === 'ok' && <CheckCircle2 color="#10B981" size={16} />}
              {field.status === 'warning' && <AlertCircle color="#D97706" size={16} />}
              {field.status === 'unclear' && (
                <span style={{ fontSize: '0.62rem', backgroundColor: '#FEF3C7', color: '#92400E', padding: '2px 5px', borderRadius: '4px' }}>
                  Unclear
                </span>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Warning Banner matching reference image */}
      {isMismatch && (
        <div
          style={{
            padding: '10px 14px',
            marginBottom: '14px',
            borderRadius: '12px',
            backgroundColor: '#FFFBEB',
            border: '1px solid #FDE68A',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          <AlertCircle color="#D97706" size={16} style={{ flexShrink: 0 }} />
          <span style={{ color: '#92400E', fontWeight: 600, fontSize: '0.8rem', lineHeight: 1.3 }}>
            {mismatches[0] || "Patient name doesn't match your claim. Continue or re-upload?"}
          </span>
        </div>
      )}

      {/* Action Buttons matching reference image */}
      <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        <button
          disabled={disabled}
          onClick={() => onSend('ACCEPT_EXTRACTION')}
          style={{
            flex: '1 1 100%',
            minHeight: '44px',
            backgroundColor: '#0052CC',
            color: '#FFFFFF',
            borderRadius: '20px',
            padding: '10px 20px',
            border: 'none',
            fontWeight: 600,
            fontSize: '0.85rem',
            cursor: 'pointer',
          }}
        >
          Details are correct
        </button>

        <button
          disabled={disabled}
          onClick={() => onSend('REUPLOAD_DOC')}
          style={{
            flex: '1 1 100%',
            minHeight: '44px',
            backgroundColor: 'transparent',
            color: '#0052CC',
            borderColor: '#0052CC',
            borderRadius: '20px',
            padding: '10px 20px',
            border: '1px solid #0052CC',
            fontWeight: 600,
            fontSize: '0.85rem',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px',
          }}
        >
          <RefreshCw size={14} />
          Re-upload
        </button>
      </div>

      {/* Footer Disclaimer */}
      <span style={{ display: 'block', marginTop: '16px', fontSize: '0.725rem', color: '#64748B' }}>
        ⓘ Details were read automatically from your document. Final assessment is done by our claims team.
      </span>
    </div>
  );
};
