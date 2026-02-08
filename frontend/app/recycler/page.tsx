"use client"

import { useState, useEffect } from "react"
import { CheckCircle2, Loader2, Landmark, ArrowRight } from "lucide-react"

export default function Page3() {
  const [data, setData] = useState({
    reward: 0,
    wallet: "",
    nft_address: ""
  })
  
  const [status, setStatus] = useState<"loading" | "idle" | "processing" | "success" | "error">("loading")
  const [signature, setSignature] = useState("")

  // 1. Automatically fetch the latest scan result from Backend
  useEffect(() => {
    const fetchLatestScan = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/last-scan")
        const json = await res.json()
        
        setData({
          reward: json.reward_sol,
          wallet: json.collector_wallet,
          nft_address: json.nft_address
        })
        setStatus("idle")
      } catch (err) {
        console.error("Data sync failed", err)
        setStatus("error")
      }
    }
    fetchLatestScan()
  }, [])

  // 2. Trigger automated payout via FastAPI
  const handlePayout = async () => {
    setStatus("processing")
    try {
      const response = await fetch("http://localhost:8000/confirm_recycle", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          nft_address: data.nft_address,
          collector_wallet: data.wallet,
          amount: data.reward
        })
      })

      const result = await response.json()
      if (result.status === "success") {
        setSignature(result.signature)
        setStatus("success")
      } else {
        setStatus("error")
      }
    } catch (err) {
      setStatus("error")
    }
  }

  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center p-6">
      <div className="max-w-md w-full bg-[#111827] border border-gray-800 rounded-[2.5rem] p-8 shadow-2xl">
        
        {status === "loading" && (
          <div className="text-center py-12">
            <Loader2 className="animate-spin text-blue-500 mx-auto mb-4" size={40} />
            <p className="text-gray-400 font-medium">Connecting to UN System...</p>
          </div>
        )}

        {status === "idle" && (
          <div className="text-center">
            <div className="w-16 h-16 bg-blue-600/20 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <Landmark className="text-blue-500" size={32} />
            </div>
            
            <h1 className="text-2xl font-bold mb-2">Recycler Confirmation</h1>
            <p className="text-gray-400 text-sm mb-8 font-medium">Verification successful via cNFT Proof.</p>
            
            <div className="bg-black/40 rounded-3xl p-6 mb-8 border border-white/5 text-left space-y-4">
              <div className="flex justify-between items-end">
                <span className="text-gray-400 text-sm font-semibold uppercase tracking-wider">Estimated Reward</span>
                <div className="text-right">
                  <span className="text-[#22c55e] text-4xl font-black">{data.reward}</span>
                  <span className="text-[#22c55e] ml-2 font-bold text-xl">SOL</span>
                </div>
              </div>

              <div className="pt-4 border-t border-white/10">
                <p className="text-[10px] text-gray-500 uppercase tracking-widest mb-2 font-bold">Collector Wallet</p>
                <p className="text-blue-300 font-mono text-[11px] truncate bg-blue-500/5 p-2 rounded-lg border border-blue-500/10">
                  {data.wallet}
                </p>
              </div>
            </div>

            <button 
              onClick={handlePayout}
              className="w-full bg-blue-600 hover:bg-blue-700 py-5 rounded-2xl font-bold flex items-center justify-center gap-3 transition-all active:scale-95 shadow-[0_0_25px_rgba(37,99,235,0.4)] text-lg"
            >
              Claim Reward <ArrowRight size={20} />
            </button>
          </div>
        )}

        {status === "processing" && (
          <div className="text-center py-12">
            <div className="relative w-20 h-20 mx-auto mb-6">
              <div className="absolute inset-0 border-4 border-blue-500/20 rounded-full"></div>
              <div className="absolute inset-0 border-4 border-t-blue-500 rounded-full animate-spin"></div>
            </div>
            <h2 className="text-xl font-bold tracking-tight">Processing Payment</h2>
            <p className="text-gray-400 text-sm mt-3 font-mono opacity-80">UN Address is signing transaction...</p>
          </div>
        )}

        {status === "success" && (
          <div className="text-center">
            <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-6 shadow-[0_0_40px_rgba(34,197,94,0.2)]">
              <CheckCircle2 className="text-green-500" size={48} />
            </div>
            <h1 className="text-2xl font-bold mb-2">SOL Dispatched!</h1>
            <p className="text-gray-400 text-sm mb-8 font-medium">Funds have been sent to your wallet. Check Phantom!</p>
            
            <div className="bg-black/60 p-5 rounded-2xl border border-gray-800 mb-8 overflow-hidden">
              <p className="text-[10px] text-gray-500 text-left mb-2 font-bold tracking-widest uppercase">Transaction Signature</p>
              <p className="text-blue-400 font-mono text-[10px] break-all text-left leading-relaxed">{signature}</p>
            </div>

            <button 
              onClick={() => window.location.href = "/"}
              className="w-full bg-gray-800 hover:bg-gray-700 py-4 rounded-2xl font-bold transition-all text-sm tracking-wide"
            >
              Return to Home
            </button>
          </div>
        )}

        {status === "error" && (
          <div className="text-center py-10">
            <div className="text-red-500 text-6xl mb-6">⚠️</div>
            <h2 className="text-xl font-bold mb-2">Payout Failed</h2>
            <p className="text-gray-400 text-sm mb-8">System busy or insufficient UN reserves. Please try again.</p>
            <button 
              onClick={() => setStatus("idle")} 
              className="px-8 py-3 bg-white/5 border border-white/10 rounded-xl text-blue-400 font-bold hover:bg-white/10 transition-all"
            >
              Retry Claim
            </button>
          </div>
        )}

      </div>
    </div>
  )
}