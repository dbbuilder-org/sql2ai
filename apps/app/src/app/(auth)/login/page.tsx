import { SignIn } from '@clerk/nextjs';

export default function LoginPage() {
  return (
    <div className="flex flex-col items-center">
      <div className="mb-8 text-center">
        <h1 className="text-2xl font-bold">Welcome back</h1>
        <p className="text-muted-foreground">Sign in to your SQL2.AI account</p>
      </div>
      <SignIn
        appearance={{
          elements: {
            rootBox: 'w-full',
            card: 'w-full shadow-none',
          },
        }}
        redirectUrl="/"
        signUpUrl="/signup"
      />
    </div>
  );
}
