"use client"
import { useState } from 'react'
import { Loader2, CheckCircle2, ExternalLink, MapPin, Trophy, Camera } from 'lucide-react'

export default function DetectionPage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleDetection = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/process_detection', {
        method: 'POST',
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Detection failed:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 p-8">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* HEADER SECTION */}
        <div className="flex justify-between items-end bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <div>
            <h1 className="text-4xl font-bold text-white mb-1">Ghost-Ray Detector</h1>
            <p className="text-slate-400">Real-time Marine Debris Analysis & Reward System</p>
          </div>
          <div className="text-right">
            <p className="text-xs font-medium text-slate-500 uppercase mb-1">Network Status</p>
            <div className="flex items-center gap-2 text-emerald-400 font-medium">
              <div className="w-2 h-2 bg-emerald-400 rounded-full" /> Solana Devnet
            </div>
          </div>
        </div>

        {/* CAMERA VIEWPORT */}
        <div className="relative aspect-video bg-slate-900 rounded-2xl overflow-hidden border border-slate-800">
          <img src="http://localhost:8000/video_feed" className="w-full h-full object-cover" alt="AI Feed" />
          <div className="absolute top-4 left-4 bg-slate-900/90 px-3 py-2 rounded-lg flex items-center gap-2 border border-slate-700">
            <Camera size={16} className="text-purple-400" />
            <span className="text-white text-xs font-medium">Live AI Stream</span>
          </div>
        </div>

        {/* ACTION BUTTON */}
        <button 
          onClick={handleDetection}
          disabled={loading}
          className="w-full py-5 bg-purple-600 hover:bg-purple-700 disabled:bg-slate-800 disabled:text-slate-500 rounded-xl font-bold text-white text-xl transition-all flex items-center justify-center gap-3"
        >
          {loading ? <><Loader2 className="animate-spin" /> Analyzing Impact...</> : "Collect & Claim Reward"}
        </button>

        {/* RESULT DISPLAY */}
        {result && result.status === "success" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Intelligence Card */}
            <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl space-y-4">
               <div className="flex items-center gap-2 text-purple-400 font-semibold text-sm">
                 <MapPin size={16}/> Intelligence Report
               </div>
               <div className="space-y-3">
                  <div className="flex justify-between items-center py-3 border-b border-slate-800">
                     <span className="text-slate-400 text-sm">Region</span>
                     <span className="text-white font-semibold">{result.location}</span>
                  </div>
                  <div className="flex justify-between items-center py-3 border-b border-slate-800">
                     <span className="text-slate-400 text-sm">Estimated Mass</span>
                     <span className="text-white font-semibold">{result.weight} Kg</span>
                  </div>
                  <div className="flex justify-between items-center py-3">
                     <span className="text-slate-400 text-sm">UN Multiplier</span>
                     <span className="text-yellow-400 font-bold">{result.multiplier}x</span>
                  </div>
               </div>
            </div>

            {/* Settlement Card */}
            <div className="bg-purple-600 p-6 rounded-2xl text-white space-y-5">
               <div className="flex justify-between items-start">
                  <div className="bg-white/20 p-3 rounded-lg">
                     <Trophy size={28} />
                  </div>
                  <div className="text-right">
                     <p className="text-xs font-medium opacity-80 uppercase mb-1">Payout Success</p>
                     <h4 className="text-3xl font-bold">+{result.reward_sol.toFixed(4)} SOL</h4>
                  </div>
               </div>
               
               <div className="bg-purple-900/40 p-4 rounded-lg space-y-1">
                  <p className="text-xs font-medium opacity-70">NFT Certificate Minted</p>
                  <p className="text-xs font-mono truncate opacity-90">{result.nft_address}</p>
               </div>

               <div className="flex gap-3">
                  <a href={`https://explorer.solana.com/tx/${result.signature}?cluster=devnet`} target="_blank" className="flex-1 bg-purple-900 hover:bg-purple-800 text-center py-3 rounded-lg text-xs font-semibold transition-all flex items-center justify-center gap-2">
                    TX Proof <ExternalLink size={12}/>
                  </a>
                  <a href={`https://explorer.solana.com/address/${result.nft_address}?cluster=devnet`} target="_blank" className="flex-1 bg-white hover:bg-slate-100 text-purple-600 text-center py-3 rounded-lg text-xs font-semibold transition-all flex items-center justify-center gap-2">
                    View NFT <ExternalLink size={12}/>
                  </a>
               </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}