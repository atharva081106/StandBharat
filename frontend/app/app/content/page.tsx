import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { mockContent } from '@/lib/mock/data'

export default function Content() {
  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[var(--color-border-primary)] pb-6">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight text-[var(--color-text-primary)]">Content Studio</h1>
          <p className="text-[var(--color-text-tertiary)] text-lg mt-1">All AI-generated and human marketing content in one place.</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" className="hidden sm:inline-flex">Filter</Button>
          <Button>+ New Content</Button>
        </div>
      </div>
      
      <div className="bg-[var(--color-bg-surface)] border border-[var(--color-border-primary)] rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left whitespace-nowrap">
            <thead className="bg-[var(--color-bg-subtle)] text-[var(--color-text-muted)] border-b border-[var(--color-border-primary)] text-xs uppercase tracking-wider font-semibold">
              <tr>
                <th className="px-6 py-4">Title</th>
                <th className="px-6 py-4">Type</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Author</th>
                <th className="px-6 py-4 text-right">Updated</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--color-border-primary)]">
              {mockContent.map((item) => (
                <tr key={item.id} className="hover:bg-[var(--color-bg-subtle)] transition-colors cursor-pointer">
                  <td className="px-6 py-4">
                    <span className="font-semibold text-[var(--color-text-primary)]">{item.title}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-[var(--color-text-secondary)]">{item.type}</span>
                  </td>
                  <td className="px-6 py-4">
                    <Badge variant={item.status === 'PUBLISHED' ? 'success' : item.status === 'DRAFT' ? 'warning' : 'secondary'} className="text-[10px] uppercase tracking-wider">
                      {item.status}
                    </Badge>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <div className="h-5 w-5 rounded-full bg-[var(--color-border-primary)] flex items-center justify-center text-[10px] font-bold text-[var(--color-text-secondary)]">
                        {item.author === 'AI Writer' ? 'AI' : item.author.charAt(0)}
                      </div>
                      <span className="text-[var(--color-text-secondary)]">{item.author}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-right text-[var(--color-text-tertiary)]">
                    {item.updated}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {mockContent.length === 0 && (
          <div className="flex flex-col items-center justify-center py-16 text-center px-4">
            <p className="text-[var(--color-text-primary)] font-medium">No content yet</p>
            <p className="text-sm text-[var(--color-text-tertiary)] mt-1">Create your first piece of content to get started.</p>
            <Button variant="outline" className="mt-4">Create Content</Button>
          </div>
        )}
      </div>
    </div>
  )
}
