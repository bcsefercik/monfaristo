import { authOptions } from "@/app/api/auth/[...nextauth]/route"
import CumulativeTickerHoldings from "@/app/components/cumulative-ticker-holdings/cumulative-ticker-holdings"
import { getServerSession } from "next-auth/next"
import type { NextRequest } from "next/server"

export default async function Protected (req: NextRequest): Promise<any> {
  const session = await getServerSession(authOptions)

  return (
    <main className="p-4 md:p-10 mx-auto max-w-7xl">
      <div>
        {
          (session !== null && session !== undefined)
            ? <div className='leading-loose text-[2rem] font-extrabold text-accent'>
                Hi {session?.user?.email}!
              </div>
            : <a className='btn btn-primary' href='/api/auth/signin'>Sign in</a>
        }
      </div>
      {session !== null && session !== undefined && <CumulativeTickerHoldings />}
    </main>
  )
}