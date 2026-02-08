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
    <div className="min-h-screen bg-black text-white p-8">
      {/* Header Impact */}
      <div className="max-w-6xl mx-auto mb-12 flex justify-between items-end">
        <div>
          <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
            <ShieldCheck className="text-blue-400" size={40} />
            Environmental Impact
          </h1>
          <p className="text-gray-400 text-lg">Every NFT represents verified plastic waste removed from the ocean.</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-500 uppercase tracking-widest mb-1">Total Debris Collected</p>
          <p className="text-5xl font-mono text-blue-400 font-bold">{totalWeight.toFixed(3)} <span className="text-2xl">KG</span></p>
        </div>
      </div>

      {/* Grid NFTs */}
      {loading ? (
        <div className="flex flex-col items-center justify-center h-64">
          <Loader2 className="animate-spin text-blue-500 mb-4" size={48} />
          <p>Scanning Blockchain for Proof of Impact...</p>
        </div>
      ) : error ? (
        <div className="bg-red-900/20 border border-red-500 p-6 rounded-lg text-center">
          <p className="text-red-400 mb-4">{error}</p>
          <button onClick={fetchNFTs} className="bg-red-500 hover:bg-red-600 px-6 py-2 rounded-full flex items-center gap-2 mx-auto">
            <RefreshCw size={18} /> Retry
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
          {nfts.map((nft) => (
            <div key={nft.mint} className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden hover:border-blue-500 transition-all group">
              <div className="aspect-square relative overflow-hidden">
                <img src={nft.image} alt={nft.name} className="object-cover w-full h-full group-hover:scale-110 transition-transform duration-500" />
                <div className="absolute top-2 right-2 bg-black/60 backdrop-blur-md px-2 py-1 rounded text-xs border border-white/20">
                  cNFT
                </div>
              </div>
              <div className="p-4">
                <h3 className="font-bold text-lg mb-2 truncate">{nft.name}</h3>
                <div className="space-y-1 mb-4">
                  {nft.attributes.slice(0, 3).map((attr: any, idx: number) => (
                    <div key={idx} className="flex justify-between text-xs">
                      <span className="text-gray-500">{attr.trait_type}</span>
                      <span className="text-blue-300 font-mono">{attr.value}</span>
                    </div>
                  ))}
                </div>
                <a 
                  href={`https://xray.helios.xyz/token/${nft.mint}?network=devnet`}
                  target="_blank"
                  className="w-full bg-gray-800 hover:bg-blue-600 py-2 rounded-lg flex items-center justify-center gap-2 text-sm transition-colors"
                >
                  View Proof <ExternalLink size={14} />
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}