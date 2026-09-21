import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

interface DynamicDataViewProps {
  data: any[];
  title?: string;
}

export default function DynamicDataView({ data, title = "Query Results" }: DynamicDataViewProps) {
  if (!data || !Array.isArray(data) || data.length === 0) return null;

  // Simple heuristic: if data objects have a numeric value, chart it. Otherwise, table.
  const sample = data[0];
  const keys = Object.keys(sample);
  const numericKey = keys.find(k => typeof sample[k] === 'number');
  const labelKey = keys.find(k => k !== numericKey) || keys[0];

  const shouldChart = !!numericKey && data.length > 1;

  return (
    <div className="glass rounded-xl p-6 animate-fade-in flex flex-col h-full">
      <h3 className="text-xl font-semibold mb-4 text-primary">{title}</h3>
      
      <div className="flex-1 min-h-[300px]">
        {shouldChart ? (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
              <XAxis dataKey={labelKey} stroke="#888" tick={{ fill: '#888' }} />
              <YAxis stroke="#888" tick={{ fill: '#888' }} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#171717', borderColor: '#333', borderRadius: '8px' }}
                itemStyle={{ color: '#3b82f6' }}
              />
              <Bar dataKey={numericKey} fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="overflow-x-auto h-full">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/10">
                  {keys.map(key => (
                    <th key={key} className="p-3 text-textMuted font-medium uppercase text-xs tracking-wider">
                      {key}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.map((row, idx) => (
                  <tr key={idx} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    {keys.map(key => (
                      <td key={key} className="p-3 text-sm">{row[key]}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
