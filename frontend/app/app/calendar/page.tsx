"use client"

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ApiClient } from '@/lib/api/client'
import { useAppProvider } from '@/lib/providers'
import {
  Calendar as CalendarIcon,
  ChevronLeft,
  ChevronRight,
  Plus,
  RefreshCw,
  Clock,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  Filter,
  Send,
  X
} from 'lucide-react'

interface PublicationEvent {
  id: string
  content_draft_id: string
  title: string
  platform: string
  status: 'SCHEDULED' | 'PUBLISHED' | 'FAILED' | 'DRAFT'
  scheduled_for: string
  published_at?: string | null
  error_message?: string | null
}

export default function CalendarPage() {
  const { auth } = useAppProvider()
  const { activeBrand } = auth
  const [currentDate, setCurrentDate] = useState(new Date())
  const [events, setEvents] = useState<PublicationEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedEvent, setSelectedEvent] = useState<PublicationEvent | null>(null)
  const [selectedPlatform, setSelectedPlatform] = useState<string>('ALL')
  const [showScheduleModal, setShowScheduleModal] = useState(false)
  const [drafts, setDrafts] = useState<any[]>([])

  // Modal form state
  const [modalDraftId, setModalDraftId] = useState('')
  const [modalPlatform, setModalPlatform] = useState('linkedin')
  const [modalDate, setModalDate] = useState('')
  const [modalTime, setModalTime] = useState('14:00')
  const [submittingSchedule, setSubmittingSchedule] = useState(false)

  const fetchCalendarData = async () => {
    setLoading(true)
    try {
      const [pubs, draftsData] = await Promise.all([
        ApiClient.get<any[]>('/api/publications').catch(() => []),
        ApiClient.get<any[]>('/api/content/drafts').catch(() => [])
      ])

      const mappedEvents: PublicationEvent[] = (pubs || []).map((p: any) => {
        const matchingDraft = (draftsData || []).find((d: any) => d.id === p.content_draft_id)
        return {
          id: p.id,
          content_draft_id: p.content_draft_id,
          title: matchingDraft?.title || p.title || 'Marketing Update',
          platform: p.platform || 'linkedin',
          status: p.status || 'SCHEDULED',
          scheduled_for: p.scheduled_for || p.created_at || new Date().toISOString(),
          published_at: p.published_at,
          error_message: p.error_message
        }
      })

      setEvents(mappedEvents)
      setDrafts(draftsData || [])
    } catch (e) {
      console.error('Failed to load calendar publications:', e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCalendarData()
  }, [activeBrand])

  // Calendar helpers
  const year = currentDate.getFullYear()
  const month = currentDate.getMonth()

  const firstDayOfMonth = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ]

  const handlePrevMonth = () => {
    setCurrentDate(new Date(year, month - 1, 1))
  }

  const handleNextMonth = () => {
    setCurrentDate(new Date(year, month + 1, 1))
  }

  const handleScheduleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!modalDraftId || !modalDate) return
    setSubmittingSchedule(true)
    try {
      const scheduledDateTime = new Date(`${modalDate}T${modalTime}:00`).toISOString()
      await ApiClient.post('/api/publications', {
        content_draft_id: modalDraftId,
        platform: modalPlatform,
        status: 'SCHEDULED',
        scheduled_for: scheduledDateTime
      })
      setShowScheduleModal(false)
      setModalDraftId('')
      setModalDate('')
      await fetchCalendarData()
    } catch (e) {
      console.error('Failed to schedule publication', e)
    } finally {
      setSubmittingSchedule(false)
    }
  }

  const filteredEvents = selectedPlatform === 'ALL'
    ? events
    : events.filter(e => e.platform.toLowerCase() === selectedPlatform.toLowerCase())

  const getEventsForDay = (day: number) => {
    return filteredEvents.filter(e => {
      const eventDate = new Date(e.scheduled_for)
      return (
        eventDate.getDate() === day &&
        eventDate.getMonth() === month &&
        eventDate.getFullYear() === year
      )
    })
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PUBLISHED':
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
      case 'SCHEDULED':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30'
      case 'FAILED':
        return 'bg-red-500/20 text-red-400 border-red-500/30'
      default:
        return 'bg-amber-500/20 text-amber-400 border-amber-500/30'
    }
  }

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-[#171515] text-[#F5F3F1]">
      {/* Top Header */}
      <div className="h-[60px] border-b border-[#373333] px-6 flex items-center justify-between shrink-0 bg-[#1C1A1A]">
        <div className="flex items-center gap-3">
          <CalendarIcon className="w-5 h-5 text-[#8F0028]" />
          <div>
            <h1 className="text-[17px] font-semibold text-[#F5F3F1] leading-none">Content & Publishing Calendar</h1>
            <p className="text-[12px] text-[#A9A4A0] mt-1 leading-none">
              Orchestrate multi-channel marketing campaigns and scheduled releases
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1 bg-[#242222] border border-[#373333] rounded-lg p-1">
            <button
              onClick={() => setSelectedPlatform('ALL')}
              className={`px-2.5 py-1 text-[11px] font-medium rounded ${
                selectedPlatform === 'ALL' ? 'bg-[#8F0028] text-white' : 'text-[#A9A4A0] hover:text-[#F5F3F1]'
              }`}
            >
              All
            </button>
            {['LinkedIn', 'Twitter', 'Instagram', 'Blog'].map(plat => (
              <button
                key={plat}
                onClick={() => setSelectedPlatform(plat)}
                className={`px-2.5 py-1 text-[11px] font-medium rounded ${
                  selectedPlatform === plat ? 'bg-[#8F0028] text-white' : 'text-[#A9A4A0] hover:text-[#F5F3F1]'
                }`}
              >
                {plat}
              </button>
            ))}
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={fetchCalendarData}
            disabled={loading}
            className="border-[#373333] bg-[#242222] text-[#F5F3F1] hover:bg-[#2A2828] text-[12px]"
          >
            <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>

          <Button
            size="sm"
            onClick={() => setShowScheduleModal(true)}
            className="bg-[#8F0028] hover:bg-[#A30030] text-white text-[12px] flex items-center gap-1.5"
          >
            <Plus className="w-3.5 h-3.5" />
            Schedule Post
          </Button>
        </div>
      </div>

      {/* Main Content: Calendar Grid + Inspector Panel */}
      <div className="flex-1 flex overflow-hidden">
        {/* Calendar Grid Container */}
        <div className="flex-1 flex flex-col p-6 overflow-y-auto">
          {/* Month Navigation & Stats Header */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <h2 className="text-[18px] font-bold text-[#F5F3F1]">
                {monthNames[month]} {year}
              </h2>
              <div className="flex items-center gap-1">
                <button
                  onClick={handlePrevMonth}
                  className="p-1 rounded hover:bg-[#242222] text-[#A9A4A0] hover:text-[#F5F3F1] transition-colors"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button
                  onClick={handleNextMonth}
                  className="p-1 rounded hover:bg-[#242222] text-[#A9A4A0] hover:text-[#F5F3F1] transition-colors"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="flex items-center gap-4 text-[12px] text-[#A9A4A0]">
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-500"></span> Scheduled: {events.filter(e => e.status === 'SCHEDULED').length}
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Published: {events.filter(e => e.status === 'PUBLISHED').length}
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-red-500"></span> Failed: {events.filter(e => e.status === 'FAILED').length}
              </span>
            </div>
          </div>

          {/* Days of Week Header */}
          <div className="grid grid-cols-7 gap-2 mb-2">
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day, i) => (
              <div
                key={day}
                className={`text-center text-[11px] font-semibold uppercase tracking-wider py-1 text-[#A9A4A0] ${
                  i === 0 || i === 6 ? 'opacity-60' : ''
                }`}
              >
                {day}
              </div>
            ))}
          </div>

          {/* Days Grid */}
          <div className="grid grid-cols-7 gap-2 flex-1 auto-rows-fr">
            {/* Blank cells for offset */}
            {Array.from({ length: firstDayOfMonth }).map((_, i) => (
              <div key={`empty-${i}`} className="min-h-[100px] bg-[#1C1A1A]/30 border border-[#2D2A2A]/40 rounded-xl p-2 opacity-30" />
            ))}

            {/* Actual Days */}
            {Array.from({ length: daysInMonth }).map((_, i) => {
              const day = i + 1
              const dayEvents = getEventsForDay(day)
              const isToday =
                new Date().getDate() === day &&
                new Date().getMonth() === month &&
                new Date().getFullYear() === year

              return (
                <div
                  key={`day-${day}`}
                  className={`min-h-[110px] bg-[#1C1A1A] border rounded-xl p-2.5 flex flex-col transition-colors ${
                    isToday ? 'border-[#8F0028] bg-[#1C1A1A]/80 shadow-md' : 'border-[#373333] hover:border-[#4A4545]'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span
                      className={`text-[12px] font-semibold w-5 h-5 flex items-center justify-center rounded-full ${
                        isToday ? 'bg-[#8F0028] text-white' : 'text-[#A9A4A0]'
                      }`}
                    >
                      {day}
                    </span>
                    {dayEvents.length > 0 && (
                      <span className="text-[10px] bg-[#242222] text-[#A9A4A0] px-1.5 py-0.5 rounded font-mono">
                        {dayEvents.length}
                      </span>
                    )}
                  </div>

                  {/* Day Events list */}
                  <div className="space-y-1.5 overflow-y-auto flex-1 max-h-[120px]">
                    {dayEvents.map(evt => (
                      <div
                        key={evt.id}
                        onClick={() => setSelectedEvent(evt)}
                        className={`p-1.5 rounded-lg border text-[11px] cursor-pointer transition-all hover:scale-[1.02] ${getStatusColor(
                          evt.status
                        )}`}
                      >
                        <div className="font-medium truncate leading-tight">{evt.title}</div>
                        <div className="flex items-center justify-between mt-1 text-[9px] opacity-80 uppercase tracking-wider">
                          <span>{evt.platform}</span>
                          <span>{new Date(evt.scheduled_for).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Selected Event Side Drawer / Details Inspector */}
        {selectedEvent && (
          <div className="w-80 border-l border-[#373333] bg-[#1C1A1A] p-5 flex flex-col justify-between shrink-0">
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b border-[#373333] pb-3">
                <span className="text-[13px] font-semibold text-[#F5F3F1]">Publication Details</span>
                <button
                  onClick={() => setSelectedEvent(null)}
                  className="p-1 text-[#A9A4A0] hover:text-[#F5F3F1] rounded"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div>
                <h3 className="text-[15px] font-semibold text-[#F5F3F1] leading-tight">
                  {selectedEvent.title}
                </h3>
                <div className="flex items-center gap-2 mt-2">
                  <Badge variant="outline" className="text-[10px] uppercase font-mono bg-[#242222] border-[#373333]">
                    {selectedEvent.platform}
                  </Badge>
                  <span
                    className={`text-[10px] uppercase px-2 py-0.5 rounded border font-semibold ${getStatusColor(
                      selectedEvent.status
                    )}`}
                  >
                    {selectedEvent.status}
                  </span>
                </div>
              </div>

              <div className="space-y-2.5 text-[12px] bg-[#242222] p-3 rounded-xl border border-[#373333]">
                <div className="flex justify-between">
                  <span className="text-[#A9A4A0]">Scheduled Time:</span>
                  <span className="text-[#F5F3F1]">
                    {new Date(selectedEvent.scheduled_for).toLocaleString()}
                  </span>
                </div>
                {selectedEvent.published_at && (
                  <div className="flex justify-between">
                    <span className="text-[#A9A4A0]">Published Time:</span>
                    <span className="text-[#F5F3F1]">
                      {new Date(selectedEvent.published_at).toLocaleString()}
                    </span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-[#A9A4A0]">Draft ID:</span>
                  <span className="text-[#F5F3F1] font-mono truncate max-w-[140px]">
                    {selectedEvent.content_draft_id}
                  </span>
                </div>
              </div>

              {selectedEvent.error_message && (
                <div className="p-3 bg-red-950/40 border border-red-800 rounded-xl text-red-300 text-[11px]">
                  <p className="font-semibold mb-1">Publishing Issue:</p>
                  <p>{selectedEvent.error_message}</p>
                </div>
              )}
            </div>

            <div className="pt-4 border-t border-[#373333] space-y-2">
              <Link href={`/app/content/${selectedEvent.content_draft_id}`} className="block">
                <Button variant="outline" className="w-full text-[12px] border-[#373333] bg-[#242222] hover:bg-[#2A2828] text-[#F5F3F1] flex items-center justify-center gap-1.5">
                  <ExternalLink className="w-3.5 h-3.5" />
                  View in Content Studio
                </Button>
              </Link>
            </div>
          </div>
        )}
      </div>

      {/* Schedule Post Modal */}
      {showScheduleModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="w-full max-w-md bg-[#1C1A1A] border border-[#373333] rounded-2xl p-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-[#373333] pb-3 mb-4">
              <h3 className="text-[16px] font-semibold text-[#F5F3F1]">Schedule Publication</h3>
              <button
                onClick={() => setShowScheduleModal(false)}
                className="text-[#A9A4A0] hover:text-[#F5F3F1]"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleScheduleSubmit} className="space-y-4 text-[13px]">
              <div>
                <label className="block text-[#A9A4A0] mb-1 font-medium">Select Content Draft</label>
                <select
                  required
                  value={modalDraftId}
                  onChange={e => setModalDraftId(e.target.value)}
                  className="w-full bg-[#242222] border border-[#373333] rounded-lg p-2.5 text-[#F5F3F1] focus:outline-none focus:border-[#8F0028]"
                >
                  <option value="">-- Choose a draft --</option>
                  {drafts.map(d => (
                    <option key={d.id} value={d.id}>
                      {d.title || 'Untitled Draft'} ({d.content_type || 'POST'})
                    </option>
                  ))}
                </select>
                {drafts.length === 0 && (
                  <p className="text-[11px] text-amber-400 mt-1">
                    No drafts found. Create one in Content Studio first.
                  </p>
                )}
              </div>

              <div>
                <label className="block text-[#A9A4A0] mb-1 font-medium">Publishing Platform</label>
                <select
                  value={modalPlatform}
                  onChange={e => setModalPlatform(e.target.value)}
                  className="w-full bg-[#242222] border border-[#373333] rounded-lg p-2.5 text-[#F5F3F1] focus:outline-none focus:border-[#8F0028]"
                >
                  <option value="linkedin">LinkedIn</option>
                  <option value="twitter">Twitter / X</option>
                  <option value="instagram">Instagram</option>
                  <option value="blog">Company Blog / CMS</option>
                  <option value="meta">Meta / Facebook</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[#A9A4A0] mb-1 font-medium">Publish Date</label>
                  <input
                    type="date"
                    required
                    value={modalDate}
                    onChange={e => setModalDate(e.target.value)}
                    className="w-full bg-[#242222] border border-[#373333] rounded-lg p-2.5 text-[#F5F3F1] focus:outline-none focus:border-[#8F0028]"
                  />
                </div>
                <div>
                  <label className="block text-[#A9A4A0] mb-1 font-medium">Publish Time</label>
                  <input
                    type="time"
                    required
                    value={modalTime}
                    onChange={e => setModalTime(e.target.value)}
                    className="w-full bg-[#242222] border border-[#373333] rounded-lg p-2.5 text-[#F5F3F1] focus:outline-none focus:border-[#8F0028]"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-[#373333]">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowScheduleModal(false)}
                  className="border-[#373333] bg-[#242222] text-[#F5F3F1] hover:bg-[#2A2828]"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={submittingSchedule || !modalDraftId || !modalDate}
                  className="bg-[#8F0028] hover:bg-[#A30030] text-white"
                >
                  {submittingSchedule ? 'Scheduling...' : 'Confirm Schedule'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
