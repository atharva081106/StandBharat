"use client"
import { useState, useEffect } from 'react'
import { useBrandBrain } from '@/lib/providers/MockProvider'
import { Plus, Loader2 } from 'lucide-react'

export function ProductsPanel() {
  const { brandBrain, loading } = useBrandBrain()
  const [products, setProducts] = useState<any[]>([])

  useEffect(() => {
    if (brandBrain?.products) {
      setProducts(brandBrain.products)
    }
  }, [brandBrain])

  if (loading) {
    return (
      <div className="flex-1 flex flex-col h-full bg-[#1C1A1A] p-8 overflow-y-auto custom-scrollbar justify-center items-center">
        <Loader2 className="w-6 h-6 text-[#A9A4A0] animate-spin" />
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col h-full bg-[#1C1A1A] p-8 overflow-y-auto custom-scrollbar">
      <div className="mb-6">
        <h2 className="text-[20px] font-bold text-[#F5F3F1] mb-1">Products & Services</h2>
        <p className="text-[13px] text-[#A9A4A0]">
          Manage your catalog of offerings and their unique selling propositions.
        </p>
      </div>
      
      <div className="space-y-6">
        <div className="bg-[#242222] border border-[#373333] rounded-xl p-5">
          <h3 className="text-sm font-bold text-[#F5F3F1] mb-4">Core Offerings</h3>
          
          <div className="space-y-3">
            {products.length === 0 ? (
              <p className="text-[12px] text-[#A9A4A0] italic">No products defined yet.</p>
            ) : (
              products.map((product: any, index: number) => (
                <div key={product.id || index} className="bg-[#1C1A1A] border border-[#373333] p-4 rounded-lg flex items-center justify-between">
                  <div>
                    <h4 className="text-[13px] font-bold text-white">{product.name}</h4>
                    <p className="text-[12px] text-[#A9A4A0] mt-1">{product.description}</p>
                  </div>
                </div>
              ))
            )}
          </div>
          
          <button className="mt-4 text-[12px] font-semibold text-[#F5F3F1] border border-[#373333] px-3 py-1.5 rounded flex items-center gap-2 hover:bg-[#373333] transition-colors">
            <Plus className="w-3.5 h-3.5" /> Add Product
          </button>
        </div>
      </div>
    </div>
  )
}
