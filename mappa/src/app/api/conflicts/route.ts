import { NextResponse } from 'next/server';
import type { ConflictZone } from '@/types';

// Import JSON data
const conflictData = require('@/../../public/data/conflicts.json');

export async function GET() {
  // In production, this could fetch from ACLED API or UCDP
  // For now, we serve static data with simulated updates
  const conflicts: ConflictZone[] = conflictData.map((c: Record<string, unknown>) => ({
    ...c,
    type: c.type as ConflictZone['type'],
    status: c.status as ConflictZone['status'],
    intensity: c.intensity as ConflictZone['intensity'],
    lastUpdate: new Date().toISOString(),
  }));
  
  return NextResponse.json({
    conflicts,
    totalCount: conflicts.length,
    lastUpdate: new Date().toISOString(),
  });
}
