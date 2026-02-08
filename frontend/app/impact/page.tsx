"use client"

import { useState, useEffect } from "react"
import { ShieldCheck, Loader2, ExternalLink, RefreshCw, Trash2 } from "lucide-react"

export default function ImpactPage() {
  const [nfts, setNfts] = useState<any[]>([])
  const [totalWeight, setTotalWeight] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const SHYFT_API_KEY = process.env.NEXT_PUBLIC_SHYFT_API_KEY || ""
  const WALLET_ADDRESS = process.env.NEXT_PUBLIC_COLLECTOR_WALLET_ADDRESS || ""

  const fetchNFTs = async () => {
    setLoading(true)
    setError(null)

    try {
      if (!SHYFT_API_KEY) throw new Error("Missing Shyft API Key")
      if (!WALLET_ADDRESS) throw new Error("Missing Wallet Address")

      // SOLUSI ERROR 417: Pindahkan API Key dari Header ke Query Parameter
      const url = `https://api.shyft.to/sol/v1/nft/compressed/read_all?network=devnet&wallet_address=${WALLET_ADDRESS.trim()}&api_key=${SHYFT_API_KEY.trim()}`;

      const res = await fetch(url, {
        method: "GET",
        headers: {
          "Accept": "application/json"
          // Tidak menggunakan x-api-key di sini untuk menghindari handshake error 417
        }
      })

      if (!res.ok) {
        const errorData = await res.json()
        throw new Error(errorData.message || `HTTP Error ${res.status}`)
      }

      const responseData = await res.json()
      const items = responseData.result || []
      
      const normalized = items.map((item: any) => ({
        mint: item.mint || item.asset_id,
        name: item.name || "GhostRay Impact",
        image: item.image_uri || "/placeholder-shark.png",
        attributes: item.attributes || []
      }))

      setNfts(normalized)

      // Menghitung Total Berat
      let weightSum = 0
      normalized.forEach((nft: any) => {
        const attr = nft.attributes?.find(
          (a: any) => a.trait_type === "Mass"
        )
        if (attr) {
          // Menghilangkan satuan 'kg' jika ada, lalu diconvert ke float
          const val = parseFloat(String(attr.value).replace(/[^\d.]/g, ''))
          if (!isNaN(val)) weightSum += val
        }
      })

      setTotalWeight(weightSum)

    } catch (err: any) {
      console.error("GALLERY FETCH ERROR:", err)
      setError(err.message || "Failed to load impact data")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchNFTs()
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-900 text-white relative overflow-hidden">
      {/* Animated Background Effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-fuchsia-600/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 w-96 h-96 bg-violet-600/5 rounded-full blur-3xl animate-pulse delay-500"></div>
      </div>

      <div className="relative z-10 p-8">
        {/* Header Impact */}
        <div className="max-w-7xl mx-auto mb-16">
          <div className="backdrop-blur-xl bg-gradient-to-r from-purple-900/30 via-fuchsia-900/20 to-purple-900/30 border border-purple-500/30 rounded-3xl p-8 shadow-2xl shadow-purple-900/50">
            <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-8">
              <div className="flex-1">
                <div className="flex items-center gap-4 mb-4">
                  <div className="p-3 bg-gradient-to-br from-purple-600 to-fuchsia-600 rounded-2xl shadow-lg shadow-purple-500/50">
                    <ShieldCheck className="text-white" size={32} />
                  </div>
                  <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-300 via-fuchsia-300 to-purple-300 bg-clip-text text-transparent">
                    Environmental Impact
                  </h1>
                </div>
                <p className="text-purple-200/80 text-lg ml-1">
                  Every NFT represents verified ocean debris collected by GhostRay marine conservation efforts
                </p>
              </div>
              
              <div className="backdrop-blur-md bg-gradient-to-br from-purple-600/20 to-fuchsia-600/20 border border-purple-400/40 rounded-2xl p-6 shadow-xl min-w-[280px]">
                <div className="flex items-center gap-3 mb-2">
                  <Trash2 className="text-fuchsia-400" size={24} />
                  <p className="text-sm text-purple-300 uppercase tracking-widest font-semibold">Total Debris Collected</p>
                </div>
                <p className="text-6xl font-mono bg-gradient-to-r from-purple-300 to-fuchsia-300 bg-clip-text text-transparent font-bold">
                  {totalWeight.toFixed(3)}
                  <span className="text-2xl ml-2 text-purple-400">KG</span>
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Grid NFTs */}
        {loading ? (
          <div className="flex flex-col items-center justify-center h-96">
            <div className="relative">
              <Loader2 className="animate-spin text-purple-500 mb-4" size={64} />
              <div className="absolute inset-0 bg-purple-500/20 rounded-full blur-xl animate-pulse"></div>
            </div>
            <p className="text-purple-200 text-lg font-medium mt-4">Scanning Blockchain for Proof of Impact...</p>
            <div className="w-48 h-1 bg-purple-900/50 rounded-full mt-4 overflow-hidden">
              <div className="h-full bg-gradient-to-r from-purple-600 to-fuchsia-600 rounded-full animate-pulse"></div>
            </div>
          </div>
        ) : error ? (
          <div className="max-w-2xl mx-auto">
            <div className="backdrop-blur-xl bg-gradient-to-r from-red-900/30 to-fuchsia-900/30 border border-red-500/50 p-8 rounded-2xl text-center shadow-2xl shadow-red-900/50">
              <div className="w-16 h-16 bg-gradient-to-br from-red-600 to-fuchsia-600 rounded-full mx-auto mb-4 flex items-center justify-center">
                <ExternalLink className="text-white" size={32} />
              </div>
              <p className="text-red-300 mb-6 text-lg">{error}</p>
              <button 
                onClick={fetchNFTs} 
                className="bg-gradient-to-r from-red-600 to-fuchsia-600 hover:from-red-700 hover:to-fuchsia-700 px-8 py-3 rounded-full flex items-center gap-3 mx-auto font-semibold shadow-lg shadow-red-900/50 transition-all hover:scale-105"
              >
                <RefreshCw size={20} /> Retry Connection
              </button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 max-w-7xl mx-auto">
            {nfts.map((nft, index) => (
              <div 
                key={nft.mint} 
                className="group backdrop-blur-md bg-gradient-to-br from-slate-900/80 to-purple-900/40 border border-purple-500/30 rounded-2xl overflow-hidden hover:border-fuchsia-500/60 transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-purple-900/50"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <div className="aspect-square relative overflow-hidden">
                  <img 
                    src={nft.image} 
                    alt={nft.name} 
                    className="object-cover w-full h-full group-hover:scale-110 transition-transform duration-700" 
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-purple-900/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  <div className="absolute top-3 right-3 backdrop-blur-md bg-gradient-to-br from-purple-600/80 to-fuchsia-600/80 px-3 py-1.5 rounded-lg text-xs font-bold border border-white/30 shadow-lg">
                    cNFT
                  </div>
                </div>
                
                <div className="p-5">
                  <h3 className="font-bold text-xl mb-3 truncate bg-gradient-to-r from-purple-200 to-fuchsia-200 bg-clip-text text-transparent">
                    {nft.name}
                  </h3>
                  
                  <div className="space-y-2 mb-5">
                    {nft.attributes.slice(0, 3).map((attr: any, idx: number) => (
                      <div 
                        key={idx} 
                        className="flex justify-between items-center text-sm backdrop-blur-sm bg-purple-900/20 px-3 py-2 rounded-lg border border-purple-700/30"
                      >
                        <span className="text-purple-400 font-medium">{attr.trait_type}</span>
                        <span className="text-fuchsia-300 font-mono font-semibold">{attr.value}</span>
                      </div>
                    ))}
                  </div>
                  
                  <a 
                    href={`https://xray.helios.xyz/token/${nft.mint}?network=devnet`}
                    target="_blank"
                    className="w-full bg-gradient-to-r from-purple-600 to-fuchsia-600 hover:from-purple-700 hover:to-fuchsia-700 py-3 rounded-xl flex items-center justify-center gap-2 text-sm font-semibold transition-all shadow-lg shadow-purple-900/50 hover:shadow-xl hover:shadow-fuchsia-900/50"
                  >
                    View Proof <ExternalLink size={16} />
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}