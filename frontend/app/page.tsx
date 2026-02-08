"use client"
import { useState } from 'react'
import { Loader2, CheckCircle2, ExternalLink, MapPin, Trophy, Camera } from 'lucide-react'

export default function DetectionPage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleDetection = async () => {
    setLoading(true);
    try {
      // 1. Trigger the Backend Process
      const response = await fetch('http://localhost:8000/process_detection', {
        method: 'POST',
      });
      const data = await response.json();
      
      // 2. Save the result (Location, Weight, Multiplier, Signature)
      setResult(data);
    } catch (error) {
      console.error("Detection failed:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-8">
      {/* HEADER SECTION */}
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-4xl font-black text-white italic tracking-tighter">GHOST-RAY DETECTOR</h1>
          <p className="text-slate-400 font-medium">Real-time Marine Debris Analysis & Reward System</p>
        </div>
        <div className="text-right">
          <p className="text-[10px] font-bold text-blue-400 uppercase tracking-widest">Network Status</p>
          <div className="flex items-center gap-2 text-emerald-400 font-bold">
            <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" /> Solana Devnet
          </div>
        </div>
      </div>

      {/* CAMERA VIEWPORT */}
      <div className="relative aspect-video bg-slate-950 rounded-[2.5rem] overflow-hidden border-4 border-slate-800 shadow-2xl">
        <img src="http://localhost:8000/video_feed" className="w-full h-full object-cover" alt="AI Feed" />
        <div className="absolute top-6 left-6 bg-black/60 backdrop-blur-md px-4 py-2 rounded-full flex items-center gap-2 border border-white/10">
          <Camera size={16} className="text-red-500 animate-pulse" />
          <span className="text-white text-xs font-bold tracking-widest uppercase">Live AI Stream</span>
        </div>
      </div>

      {/* ACTION BUTTON */}
      <button 
        onClick={handleDetection}
        disabled={loading}
        className="w-full py-6 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 rounded-3xl font-black text-white text-2xl transition-all shadow-[0_0_30px_rgba(37,99,235,0.3)] flex items-center justify-center gap-4"
      >
        {loading ? <><Loader2 className="animate-spin" /> ANALYZING IMPACT...</> : "COLLECT & CLAIM REWARD"}
      </button>

      {/* RESULT DISPLAY (MUNCUL SETELAH DETEKSI) */}
      {result && result.status === "success" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-in fade-in slide-in-from-bottom-8 duration-500">
          
          {/* Economic Card */}
          <div className="bg-slate-900 p-8 rounded-[2rem] border border-slate-800 space-y-4">
             <div className="flex items-center gap-2 text-blue-400 font-bold uppercase text-xs tracking-widest">
               <MapPin size={16}/> Intelligence Report
             </div>
             <div className="space-y-4">
                <div className="flex justify-between items-center text-sm border-b border-slate-800 pb-3">
                   <span className="text-slate-400">Region</span>
                   <span className="text-white font-bold">{result.location}</span>
                </div>
                <div className="flex justify-between items-center text-sm border-b border-slate-800 pb-3">
                   <span className="text-slate-400">Estimated Mass</span>
                   <span className="text-white font-bold">{result.weight} Kg</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                   <span className="text-slate-400">UN Sustainability Multiplier</span>
                   <span className="text-yellow-400 font-black">{result.multiplier}x</span>
                </div>
             </div>
          </div>

          {/* Settlement & NFT Card */}
          <div className="bg-gradient-to-br from-blue-600 to-indigo-700 p-8 rounded-[2rem] shadow-xl text-white space-y-6">
             <div className="flex justify-between items-start">
                <div className="bg-white/20 p-3 rounded-2xl">
                   <Trophy size={32} />
                </div>
                <div className="text-right">
                   <p className="text-[10px] font-black uppercase tracking-widest opacity-70">Payout Success</p>
                   <h4 className="text-3xl font-black">+{result.reward_sol.toFixed(4)} SOL</h4>
                </div>
             </div>
             
             <div className="bg-black/20 p-4 rounded-2xl space-y-2">
                <p className="text-[10px] font-bold uppercase opacity-60">NFT Certificate Minted</p>
                <p className="text-xs font-mono truncate">{result.nft_address}</p>
             </div>

             <div className="flex gap-3">
                <a href={`https://explorer.solana.com/tx/${result.signature}?cluster=devnet`} target="_blank" className="flex-1 bg-black text-white text-center py-3 rounded-xl text-xs font-bold hover:bg-slate-900 transition-all flex items-center justify-center gap-2">
                  TX Proof <ExternalLink size={12}/>
                </a>
                <a href={`https://explorer.solana.com/address/${result.nft_address}?cluster=devnet`} target="_blank" className="flex-1 bg-white text-blue-600 text-center py-3 rounded-xl text-xs font-bold hover:bg-slate-100 transition-all flex items-center justify-center gap-2">
                  View NFT <ExternalLink size={12}/>
                </a>
             </div>
          </div>
        </div>
      )}
    </div>
  )
}