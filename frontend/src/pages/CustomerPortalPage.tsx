import React, { useState } from 'react';
import { 
  Upload, Mic, FileText, CheckCircle2, ShieldCheck, 
  Sparkles, Globe, AlertCircle, ArrowRight 
} from 'lucide-react';
import { apiClient } from '../api/client';

interface CustomerPortalPageProps {
  onClaimSubmitted: (claimId: string) => void;
}

export const CustomerPortalPage: React.FC<CustomerPortalPageProps> = ({ onClaimSubmitted }) => {
  const [policyNumber, setPolicyNumber] = useState('POL-AUTO-8821');
  const [claimantName, setClaimantName] = useState('Priya Sharma');
  const [claimType, setClaimType] = useState('Auto Collision');
  const [incidentDate, setIncidentDate] = useState('2026-10-06 15:45');
  const [incidentLocation, setIncidentLocation] = useState('Indiranagar 100ft Road, Bengaluru');
  const [description, setDescription] = useState('Another car reversed into my vehicle while backing out of a parking bay, cracking the front bumper.');
  const [claimedAmount, setClaimedAmount] = useState(45000);
  
  // Files
  const [damageFile, setDamageFile] = useState<File | null>(null);
  const [invoiceFile, setInvoiceFile] = useState<File | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [hasVoiceNote, setHasVoiceNote] = useState(false);

  // Submission state
  const [submitting, setSubmitting] = useState(false);
  const [submittedClaimId, setSubmittedClaimId] = useState<string | null>(null);
  const [language, setLanguage] = useState<'en' | 'hi' | 'kn'>('en');

  const handleRecordVoice = () => {
    setIsRecording(true);
    setTimeout(() => {
      setIsRecording(false);
      setHasVoiceNote(true);
    }, 2500);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      // 1. Create Claim
      const claimRes = await apiClient.post('/claims', {
        policy_number: policyNumber,
        claimant_name: claimantName,
        claimant_email: 'customer@insurance.ai',
        claim_type: claimType,
        incident_date: incidentDate,
        incident_location: incidentLocation,
        incident_description: description,
        claimed_amount: Number(claimedAmount),
        currency: 'INR'
      });

      const claimId = claimRes.id;
      setSubmittedClaimId(claimId);

      // 2. Upload damage file if attached
      if (damageFile) {
        const formData = new FormData();
        formData.append('file', damageFile);
        formData.append('doc_category', 'damage_photo');
        await apiClient.uploadFile(`/claims/${claimId}/documents`, formData);
      }

      // 3. Upload voice note if simulated
      if (hasVoiceNote) {
        const audioBlob = new Blob(["Simulated customer audio statement voice note."], { type: 'audio/wav' });
        const audioFile = new File([audioBlob], "customer_voice_statement.wav", { type: 'audio/wav' });
        const formData = new FormData();
        formData.append('file', audioFile);
        formData.append('doc_category', 'audio_statement');
        await apiClient.uploadFile(`/claims/${claimId}/documents`, formData);
      }

      // 4. Auto-trigger multi-agent triage
      await apiClient.post(`/claims/${claimId}/analyze`);

      onClaimSubmitted(claimId);
    } catch (err: any) {
      alert(`Submission error: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  const localizedMessages = {
    en: {
      title: "Claim Submitted Successfully",
      desc: "Our automated triage engine has received your claim dossier. You will receive real-time updates as your claim is processed.",
      est: "Estimated Turnaround: 2 to 4 hours"
    },
    hi: {
      title: "दावा सफलतापूर्वक जमा किया गया",
      desc: "हमारे स्वचालित सिस्टम को आपका दावा प्राप्त हो गया है। दावा प्रक्रिया की स्थिति आपको समय पर भेजी जाएगी।",
      est: "अनुमानित समय: 2 से 4 घंटे"
    },
    kn: {
      title: "ವಿಮಾ ಹಕ್ಕು ಯಶಸ್ವಿಯಾಗಿ ಸಲ್ಲಿಸಲಾಗಿದೆ",
      desc: "ನಮ್ಮ ಸ್ವಯಂಚಾಲಿತ ವ್ಯವಸ್ಥೆಯು ನಿಮ್ಮ ಕ್ಲೈಮ್ ಅನ್ನು ಸ್ವೀಕರಿಸಿದೆ. ಪ್ರಕ್ರಿಯೆಯ ಮಾಹಿತಿಯನ್ನು ಶೀಘ್ರದಲ್ಲೇ ನೀಡಲಾಗುವುದು.",
      est: "ಅಂದಾಜು ಸಮಯ: 2 ರಿಂದ 4 ಗಂಟೆಗಳು"
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-emerald-950 via-slate-900 to-slate-900 p-6 rounded-2xl border border-emerald-900/40 shadow-xl flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-2 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-1">
            <ShieldCheck className="w-4 h-4" />
            <span>Policyholder Self-Service Portal</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">File an Insurance Claim</h1>
          <p className="text-xs text-slate-400 mt-1">Submit damage photos, documents, and voice descriptions in minutes.</p>
        </div>

        {/* Language selector */}
        <div className="flex items-center space-x-2 bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800 text-xs">
          <Globe className="w-3.5 h-3.5 text-slate-400" />
          <select 
            value={language} 
            onChange={(e: any) => setLanguage(e.target.value)}
            className="bg-transparent text-slate-200 focus:outline-none cursor-pointer"
          >
            <option value="en" className="bg-slate-900">English</option>
            <option value="hi" className="bg-slate-900">हिंदी (Hindi)</option>
            <option value="kn" className="bg-slate-900">ಕನ್ನಡ (Kannada)</option>
          </select>
        </div>
      </div>

      {submittedClaimId ? (
        <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl shadow-2xl text-center space-y-4">
          <div className="w-16 h-16 rounded-full bg-emerald-500/10 text-emerald-400 flex items-center justify-center mx-auto border border-emerald-500/20 shadow-lg">
            <CheckCircle2 className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-bold text-white">{localizedMessages[language].title}</h2>
          <p className="text-xs text-slate-400 max-w-md mx-auto">{localizedMessages[language].desc}</p>
          <div className="inline-block font-mono text-sm px-4 py-2 rounded-xl bg-slate-950 border border-slate-800 text-blue-400 font-bold">
            Tracking ID: {submittedClaimId}
          </div>
          <p className="text-xs text-emerald-400 font-medium">{localizedMessages[language].est}</p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl space-y-5 text-xs">
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-slate-300 font-medium block mb-1">Policy Number</label>
              <input
                type="text"
                value={policyNumber}
                onChange={(e) => setPolicyNumber(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white focus:outline-none"
                required
              />
            </div>
            <div>
              <label className="text-slate-300 font-medium block mb-1">Claimant Full Name</label>
              <input
                type="text"
                value={claimantName}
                onChange={(e) => setClaimantName(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white focus:outline-none"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="text-slate-300 font-medium block mb-1">Claim Category</label>
              <select
                value={claimType}
                onChange={(e) => setClaimType(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white focus:outline-none"
              >
                <option value="Auto Collision">Auto Collision</option>
                <option value="Property Water Damage">Property Water Damage</option>
                <option value="Commercial Fire">Commercial Fire</option>
                <option value="Theft & Burglary">Theft & Burglary</option>
              </select>
            </div>
            <div>
              <label className="text-slate-300 font-medium block mb-1">Incident Date & Time</label>
              <input
                type="text"
                value={incidentDate}
                onChange={(e) => setIncidentDate(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white focus:outline-none"
                required
              />
            </div>
            <div>
              <label className="text-slate-300 font-medium block mb-1">Estimated Claim (₹ INR)</label>
              <input
                type="number"
                value={claimedAmount}
                onChange={(e) => setClaimedAmount(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white focus:outline-none font-mono"
                required
              />
            </div>
          </div>

          <div>
            <label className="text-slate-300 font-medium block mb-1">Incident Location</label>
            <input
              type="text"
              value={incidentLocation}
              onChange={(e) => setIncidentLocation(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-white focus:outline-none"
              required
            />
          </div>

          <div>
            <label className="text-slate-300 font-medium block mb-1">Incident Description</label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-white focus:outline-none"
              required
            />
          </div>

          {/* Multimodal Upload & Audio Section */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            
            {/* Image / Evidence Upload */}
            <div className="p-4 bg-slate-950 rounded-xl border border-dashed border-slate-800 text-center hover:border-slate-700 transition-all">
              <Upload className="w-6 h-6 text-blue-400 mx-auto mb-2" />
              <span className="font-semibold text-slate-200 block mb-1">Upload Damage Photos</span>
              <span className="text-[11px] text-slate-500 block mb-3">JPEG, PNG up to 25MB</span>
              <input 
                type="file" 
                accept="image/*"
                onChange={(e) => setDamageFile(e.target.files ? e.target.files[0] : null)}
                className="text-[11px] text-slate-400 file:mr-2 file:py-1 file:px-3 file:rounded-lg file:border-0 file:text-[11px] file:bg-blue-600 file:text-white cursor-pointer"
              />
              {damageFile && <p className="text-xs text-emerald-400 mt-2 font-medium">✓ {damageFile.name}</p>}
            </div>

            {/* Voice Description */}
            <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 flex flex-col items-center justify-center text-center">
              <Mic className="w-6 h-6 text-purple-400 mb-2" />
              <span className="font-semibold text-slate-200 block mb-1">Record Voice Note</span>
              <span className="text-[11px] text-slate-500 block mb-3">Describe the incident conversationally</span>
              <button
                type="button"
                onClick={handleRecordVoice}
                disabled={isRecording}
                className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                  isRecording 
                    ? 'bg-red-600 text-white animate-pulse' 
                    : hasVoiceNote 
                    ? 'bg-purple-900/60 text-purple-200 border border-purple-700' 
                    : 'bg-purple-600 hover:bg-purple-500 text-white'
                }`}
              >
                {isRecording ? 'Listening...' : hasVoiceNote ? '✓ Voice Statement Attached' : 'Record Audio Statement'}
              </button>
            </div>

          </div>

          <div className="flex justify-end pt-4 border-t border-slate-800">
            <button
              type="submit"
              disabled={submitting}
              className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs px-6 py-3 rounded-xl shadow-lg transition-all flex items-center space-x-2 disabled:opacity-50"
            >
              <Sparkles className="w-4 h-4" />
              <span>{submitting ? 'Submitting & Running Triage...' : 'Submit Claim Dossier'}</span>
            </button>
          </div>

        </form>
      )}

    </div>
  );
};
