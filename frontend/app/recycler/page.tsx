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
    <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center p-6">
      <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-3xl p-8">
        
        {status === "loading" && (
          <div className="text-center py-12">
            <Loader2 className="animate-spin text-purple-500 mx-auto mb-4" size={40} />
            <p className="text-slate-400 font-medium">Connecting to UN System...</p>
          </div>
        )}

        {status === "idle" && (
          <div className="text-center">
            <div className="w-16 h-16 bg-purple-600/20 rounded-xl flex items-center justify-center mx-auto mb-6 border border-purple-500/30">
              <Landmark className="text-purple-500" size={32} />
            </div>
            
            <h1 className="text-2xl font-bold mb-2">Recycler Confirmation</h1>
            <p className="text-slate-400 text-sm mb-8">Verification successful via cNFT Proof.</p>
            
            <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 mb-8 text-left space-y-4">
              <div className="flex justify-between items-end">
                <span className="text-slate-400 text-sm font-medium uppercase">Estimated Reward</span>
                <div className="text-right">
                  <span className="text-green-400 text-4xl font-bold">{data.reward}</span>
                  <span className="text-green-400 ml-2 font-semibold text-lg">SOL</span>
                </div>
              </div>

              <div className="pt-4 border-t border-slate-700">
                <p className="text-xs text-slate-500 uppercase mb-2 font-medium">Collector Wallet</p>
                <p className="text-purple-400 font-mono text-xs truncate bg-slate-900 p-2 rounded-lg">
                  {data.wallet}
                </p>
              </div>
            </div>

            <button 
              onClick={handlePayout}
              className="w-full bg-purple-600 hover:bg-purple-700 py-4 rounded-xl font-bold flex items-center justify-center gap-3 transition-all text-lg"
            >
              Claim Reward <ArrowRight size={20} />
            </button>
          </div>
        )}

        {status === "processing" && (
          <div className="text-center py-12">
            <div className="relative w-20 h-20 mx-auto mb-6">
              <div className="absolute inset-0 border-4 border-slate-700 rounded-full"></div>
              <div className="absolute inset-0 border-4 border-t-purple-500 rounded-full animate-spin"></div>
            </div>
            <h2 className="text-xl font-bold">Processing Payment</h2>
            <p className="text-slate-400 text-sm mt-3">UN Address is signing transaction...</p>
          </div>
        )}

        {status === "success" && (
          <div className="text-center">
            <div className="w-20 h-20 bg-green-500/20 border border-green-500/30 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle2 className="text-green-500" size={48} />
            </div>
            <h1 className="text-2xl font-bold mb-2">SOL Dispatched!</h1>
            <p className="text-slate-400 text-sm mb-8">Funds have been sent to your wallet. Check Phantom!</p>
            
            <div className="bg-slate-800 border border-slate-700 p-5 rounded-xl mb-8">
              <p className="text-xs text-slate-500 text-left mb-2 font-medium uppercase">Transaction Signature</p>
              <p className="text-purple-400 font-mono text-xs break-all text-left">{signature}</p>
            </div>

            <button 
              onClick={() => window.location.href = "/"}
              className="w-full bg-slate-800 hover:bg-slate-700 border border-slate-700 py-4 rounded-xl font-semibold transition-all"
            >
              Return to Home
            </button>
          </div>
        )}

        {status === "error" && (
          <div className="text-center py-10">
            <div className="text-red-500 text-5xl mb-6">⚠️</div>
            <h2 className="text-xl font-bold mb-2">Payout Failed</h2>
            <p className="text-slate-400 text-sm mb-8">System busy or insufficient UN reserves. Please try again.</p>
            <button 
              onClick={() => setStatus("idle")} 
              className="px-8 py-3 bg-slate-800 border border-slate-700 rounded-xl text-purple-400 font-semibold hover:bg-slate-700 transition-all"
            >
              Retry Claim
            </button>
          </div>
        )}

      </div>
    </div>
  )
}